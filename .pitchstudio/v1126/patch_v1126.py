#!/usr/bin/env python3
"""BEAT flow v1.12.6 – Linha do Tempo Inteligente: marcadores manuais persistentes.
Incremental sobre v1.12.5; sem tocar na importação/YouTube/motor de IA.
"""
from pathlib import Path
import sys
root=Path(sys.argv[1])
pkg=root/'app/src/main/java/br/com/timachado/pitchstudio'
main=pkg/'MainActivity.kt'
lib=pkg/'ProjectLibrary.kt'
wave=pkg/'ui/WaveformView.kt'
gradle=root/'app/build.gradle.kts'


def change(text,old,new,name):
    count=text.count(old)
    if count!=1: raise SystemExit(f'v1.12.6: marcador {name} esperado 1 vez, encontrado {count}: {old[:100]!r}')
    return text.replace(old,new,1)

sections='''package br.com.timachado.pitchstudio

/** Marcadores musicais manuais, não gerados por um detector automático fictício. */
internal object TimelineSections {
    val TYPES = listOf("Introdução", "Verso", "Refrão", "Ponte", "Solo", "Final")
    const val MAX = 64
    const val MIN_GAP = 0.005

    data class Marker(val fraction: Double, val label: String)

    fun normalized(items: List<Marker>): List<Marker> {
        val ordered = items.asSequence()
            .filter { it.fraction.isFinite() && it.fraction >= 0.0 && it.fraction < 1.0 }
            .map { Marker(it.fraction, it.label.trim().take(32)) }
            .filter { it.label.isNotBlank() }
            .sortedBy { it.fraction }
            .toList()
        val result = ArrayList<Marker>(MAX)
        for (item in ordered) {
            if (result.size >= MAX) break
            if (result.isEmpty() || item.fraction - result.last().fraction >= MIN_GAP)
                result.add(item)
        }
        return result
    }

    fun add(items: List<Marker>, candidate: Marker): List<Marker> {
        require(candidate.fraction.isFinite() && candidate.fraction in 0.0..<1.0)
        val name = candidate.label.trim().take(32)
        require(name.isNotBlank())
        val filtered = normalized(items).filter {
            kotlin.math.abs(it.fraction - candidate.fraction) >= MIN_GAP
        }
        require(filtered.size < MAX) { "Limite de $MAX trechos atingido." }
        return normalized(filtered + Marker(candidate.fraction, name))
    }

    fun end(items: List<Marker>, start: Double): Double =
        normalized(items).firstOrNull { it.fraction > start + MIN_GAP / 2 }?.fraction ?: 1.0
}
'''
(pkg/'TimelineSections.kt').write_text(sections,encoding='utf-8')

s=main.read_text(encoding='utf-8')
s=change(s,'    private var abcEnabled = false', '''    private var songSections: List<TimelineSections.Marker> = emptyList()
    private var timelineStatus: TextView? = null
    private var abcEnabled = false''','main section field')

# Desenho da onda permanece intacto; marcadores aparecem sobre ela.
code='''    /** Estrutura manual: introdução/versos/refrões, sem mexer nos samples. */
    private fun refreshSongSections() {
        waveform.sectionFractions = songSections.map { it.fraction }
        timelineStatus?.text = if (songSections.isEmpty())
            "Nenhum trecho marcado · posicione a música e marque"
        else if (songSections.size == 1) "1 trecho marcado · toque em Ver trechos"
        else "${songSections.size} trechos marcados · toque em Ver trechos"
    }

    private fun persistSongSections() {
        refreshSongSections()
        val id = activeProjectId ?: return
        try {
            ProjectLibrary.updateTimelineSections(this, id, songSections)
        } catch (error: Exception) {
            android.util.Log.e("BEATflow-Timeline","Falha ao salvar trechos",error)
            toast("Trechos não salvos: " + (error.message ?: "espaço insuficiente"))
        }
    }

    private fun markSongSection() {
        if (original == null) {
            toast("Importe uma música antes de marcar trechos.")
            return
        }
        MaterialAlertDialogBuilder(this).setTitle("Marcar trecho")
            .setItems(TimelineSections.TYPES.toTypedArray()) { _, selection ->
                val position=player.fraction().coerceIn(0.0,0.995)
                try {
                    songSections=TimelineSections.add(songSections,
                        TimelineSections.Marker(position, TimelineSections.TYPES[selection]))
                    persistSongSections()
                    statusLabel.text="Trecho marcado em " + formatFraction(position)
                } catch (error: Exception) {
                    toast(error.message ?: "Não foi possível marcar esse trecho.")
                }
            }.setNegativeButton("Cancelar",null).show()
    }

    private fun showSongSections() {
        if (songSections.isEmpty()) {
            MaterialAlertDialogBuilder(this).setTitle("Linha do Tempo Inteligente")
                .setMessage("Posicione o áudio na onda e toque em Marcar trecho. As partes da música são identificadas manualmente nesta versão.")
                .setPositiveButton("Entendi",null).show()
            return
        }
        val items=songSections.toList()
        val labels=items.map { it.label + " · " + formatFraction(it.fraction) }.toTypedArray()
        MaterialAlertDialogBuilder(this).setTitle("Trechos da música")
            .setItems(labels) { _, index -> songSectionActions(items[index]) }
            .setNegativeButton("Fechar",null).show()
    }

    private fun songSectionActions(marker: TimelineSections.Marker) {
        MaterialAlertDialogBuilder(this).setTitle(marker.label + " · " + formatFraction(marker.fraction))
            .setItems(arrayOf("Ir para o trecho", "Repetir este trecho", "Renomear", "Excluir marcação")) { _, action ->
                when (action) {
                    0 -> {
                        player.seekFraction(marker.fraction)
                        refreshPlayButton()
                        statusLabel.text = "Posição: " + marker.label
                    }
                    1 -> {
                        val until=TimelineSections.end(songSections,marker.fraction)
                        if (until - marker.fraction < TimelineSections.MIN_GAP) {
                            toast("Trecho curto demais para repetição.")
                        } else {
                            loopA=marker.fraction
                            loopB=until
                            player.seekFraction(marker.fraction)
                            applyLoop()
                            scheduleLibraryAutosave()
                        }
                    }
                    2 -> renameSongSection(marker)
                    3 -> {
                        songSections=songSections.filterNot { it == marker }
                        persistSongSections()
                        toast("Marcação excluída.")
                    }
                }
            }.setNegativeButton("Voltar") { _,_ -> showSongSections() }.show()
    }

    private fun renameSongSection(marker: TimelineSections.Marker) {
        val input=EditText(this).apply {
            setSingleLine(true)
            setText(marker.label)
            setSelection(text.length)
            hint="Nome do trecho"
        }
        MaterialAlertDialogBuilder(this).setTitle("Renomear trecho")
            .setView(input)
            .setNegativeButton("Cancelar",null)
            .setPositiveButton("Salvar") { _,_ ->
                val title=input.text.toString().trim().take(32)
                if(title.isBlank()) {toast("Informe um nome para o trecho.");return@setPositiveButton}
                songSections=TimelineSections.add(
                    songSections.filterNot { it==marker },
                    TimelineSections.Marker(marker.fraction,title))
                persistSongSections()
            }.show()
    }

'''
s=change(s,'    private fun markA() {', code + '    private fun markA() {','main add timeline methods')
s=change(s,'    private fun cleanupProjects() {', '''    private fun cleanupProjects() {
        songSections=emptyList()
        if (::waveform.isInitialized) refreshSongSections()''','clear timeline when song changes')
s=change(s,'                    original = project\n                    activeProjectId = entry.id', '''                    original = project
                    songSections=loaded.sections
                    refreshSongSections()
                    activeProjectId = entry.id''','reopen saved timeline')
s=change(s,'                val settings = ProjectLibrary.Settings(\n                    title, semitones', '''                val sectionsAtSave = songSections.toList()
                val settings = ProjectLibrary.Settings(
                    title, semitones''','capture saved timeline')
s=change(s,'                                    activeProjectId=entry.id\n                                    activeProjectTitle=entry.title', '''                                    activeProjectId=entry.id
                                    activeProjectTitle=entry.title
                                    persistSongSections()''','save initial markers')
# If playback source changes during async save, still store the captured previous markings.
s=change(s,'                                toast("Projeto salvo.")', '''                                if (original !== source && sectionsAtSave.isNotEmpty()) {
                                    try { ProjectLibrary.updateTimelineSections(this,entry.id,sectionsAtSave) }
                                    catch (error: Exception) {
                                        android.util.Log.w("BEATflow-Timeline","Falha ao preservar trechos no projeto salvo",error)
                                    }
                                }
                                toast("Projeto salvo.")''','persist snapshot on song switch')
s=change(s,'''                abcPanel=subPanel
                column.addView(subPanel,full(wrap()))
            }''', '''                abcPanel=subPanel
                column.addView(subPanel,full(wrap()))
                // Linha do Tempo: controles na área existente, sem reorganizar cards.
                column.addView(text("Linha do Tempo Inteligente", 16f,true),full(wrap(),top=14))
                val timelineActions=row()
                timelineActions.addView(button("Marcar trecho") { markSongSection() },
                    LinearLayout.LayoutParams(0,dp(48),1f).apply {marginEnd=dp(4)})
                timelineActions.addView(button("Ver trechos") { showSongSections() },
                    LinearLayout.LayoutParams(0,dp(48),1f).apply {marginStart=dp(4)})
                column.addView(timelineActions,full(wrap(),top=8))
                timelineStatus=text("Nenhum trecho marcado · posicione a música e marque",12f,false)
                column.addView(timelineStatus,full(wrap(),top=5))
                refreshSongSections()
            }''','add visible buttons')
main.write_text(s,encoding='utf-8')

l=lib.read_text(encoding='utf-8')
l=change(l,'    data class Opened(val project: AudioProject, val settings: Settings)', '''    data class Opened(val project: AudioProject, val settings: Settings,
                      val sections: List<TimelineSections.Marker> = emptyList())''','lib Opened')
# Structural helper to preserve all other project fields and avoid touching the PCM.
newlib='''    /** Marcadores persistentes e offline, em gravação atômica. */
    @Synchronized fun updateTimelineSections(context: Context, id: String,
            markers: List<TimelineSections.Marker>) {
        val destination=metadata(directory(context,id))
        val obj=JSONObject(destination.readText(Charsets.UTF_8))
        require(obj.getInt("schema")==1) { "Projeto incompatível." }
        val normalized=TimelineSections.normalized(markers)
        val stored=JSONArray().apply {
            for(marker in normalized) put(JSONObject().apply {
                put("fraction",marker.fraction)
                put("label",marker.label)
            })
        }
        if (obj.optJSONArray("songSections")?.toString()==stored.toString()) return
        obj.put("songSections",stored)
        obj.put("updatedAt",System.currentTimeMillis())
        val atomic=AtomicFile(destination)
        var output: FileOutputStream?=null
        try {
            output=atomic.startWrite()
            output.write(obj.toString().toByteArray(Charsets.UTF_8))
            atomic.finishWrite(output)
        } catch (error: Exception) {
            if(output!=null) atomic.failWrite(output)
            throw error
        }
    }

    private fun loadSongSections(json: JSONObject): List<TimelineSections.Marker> {
        val values=json.optJSONArray("songSections") ?: return emptyList()
        val items=ArrayList<TimelineSections.Marker>()
        for (index in 0 until minOf(values.length(),TimelineSections.MAX)) {
            val row=values.optJSONObject(index) ?: continue
            items.add(TimelineSections.Marker(
                row.optDouble("fraction",Double.NaN),row.optString("label","")))
        }
        return TimelineSections.normalized(items)
    }

'''
l=change(l,'    fun open(context: Context, id: String): Opened {',newlib+'    fun open(context: Context, id: String): Opened {','lib persistence functions')
l=change(l,'        return Opened(project, settings)', '        return Opened(project, settings,loadSongSections(obj))','lib reader')
lib.write_text(l,encoding='utf-8')

w=wave.read_text(encoding='utf-8')
w=change(w,'    var onSeek: ((Double) -> Unit)? = null', '''    var onSeek: ((Double) -> Unit)? = null
    var sectionFractions: List<Double> = emptyList()
        set(value) { field = value; invalidate() }''','wave list')
w=change(w,'        paint.strokeWidth = 3f\n        paint.color = marker', '''        // Marcadores musicais discretos sobrepostos à onda real.
        paint.color=if(dark) 0xFFBBA9FF.toInt() else 0xFF7351B2.toInt()
        paint.strokeWidth=max(1f,resources.displayMetrics.density)
        for (fraction in sectionFractions) {
            if (!fraction.isFinite() || fraction !in 0.0..1.0) continue
            val x=(fraction*width).toFloat()
            canvas.drawLine(x,0f,x,height.toFloat(),paint)
            canvas.drawCircle(x,4f*resources.displayMetrics.density,
                3f*resources.displayMetrics.density,paint)
        }
        paint.strokeWidth = 3f
        paint.color = marker''','wave drawing')
wave.write_text(w,encoding='utf-8')

tests='''package br.com.timachado.pitchstudio

import org.junit.Assert.*
import org.junit.Test

class TimelineSectionsTest {
    @Test fun ordersAndRejectsInvalidMarkers() {
        val result=TimelineSections.normalized(listOf(
            TimelineSections.Marker(.70,"Refrão"),
            TimelineSections.Marker(.20,"Verso"),
            TimelineSections.Marker(Double.NaN,"Ponte"),
            TimelineSections.Marker(1.0,"Fim inválido"),
            TimelineSections.Marker(.201,"Muito perto"),
            TimelineSections.Marker(.1,"  ")
        ))
        assertEquals(2,result.size)
        assertEquals("Verso",result[0].label)
        assertEquals(.70,result[1].fraction,0.00001)
    }
    @Test fun replacesNearDuplicateAndFindsLoopEnd() {
        val a=TimelineSections.add(emptyList(),TimelineSections.Marker(.3,"Verso"))
        val b=TimelineSections.add(a,TimelineSections.Marker(.302,"Refrão"))
        assertEquals(1,b.size)
        assertEquals("Refrão",b[0].label)
        val c=TimelineSections.add(b,TimelineSections.Marker(.66,"Ponte"))
        assertEquals(.66,TimelineSections.end(c,.302),0.00001)
        assertEquals(1.0,TimelineSections.end(c,.66),0.00001)
    }
    @Test fun limitsMarkerCountAndTrimsNames() {
        val many=(0 until 66).map {
            TimelineSections.Marker(it/70.0, "Nome longo ".repeat(10))
        }
        val result=TimelineSections.normalized(many)
        assertEquals(64,result.size)
        assertEquals(32,result.first().label.length)
    }
}
'''
testfolder=root/'app/src/test/java/br/com/timachado/pitchstudio'
(testfolder/'TimelineSectionsTest.kt').write_text(tests,encoding='utf-8')

g=gradle.read_text(encoding='utf-8')
for old,new in [('versionCode = 36','versionCode = 37'),('versionName = "1.12.5"','versionName = "1.12.6"')]:
    g=change(g,old,new,'Gradle '+old)
gradle.write_text(g,encoding='utf-8')
print('BEAT flow v1.12.6: marcadores musicais, waveform e persistência integrados.')

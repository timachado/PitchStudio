#!/usr/bin/env python3
"""BEAT flow v1.12.4: autosave e histórico offline sem mudança de layout."""
from pathlib import Path
import sys
root=Path(sys.argv[1]).resolve()
pkg=root/"app/src/main/java/br/com/timachado/pitchstudio"
main=pkg/"MainActivity.kt"; lib=pkg/"ProjectLibrary.kt"
s=main.read_text(encoding="utf-8")
l=lib.read_text(encoding="utf-8")
def change(body,old,new):
 n=body.count(old)
 if n!=1: raise SystemExit("Marcador único necessário (%d): %s"%(n,old[:85]))
 return body.replace(old,new,1)
l=change(l,"import android.content.Context\n","import android.content.Context\nimport android.util.AtomicFile\n")
l=change(l,"    data class Opened(val project: AudioProject, val settings: Settings)",
"""    data class Opened(val project: AudioProject, val settings: Settings)
    data class Revision(val savedAt: Long, val settings: Settings)""")
addlib=r'''    /** Altera somente o JSON, nunca copia ou edita o PCM original. */
    @Synchronized fun updateSettings(context: Context, id: String, settings: Settings) {
        val dir = directory(context, id)
        require(audio(dir).isFile) { "Áudio original indisponível." }
        val destination = metadata(dir)
        val obj = JSONObject(destination.readText(Charsets.UTF_8))
        require(obj.getInt("schema") == 1) { "Versão de projeto não suportada." }
        val title = settings.title.trim().take(100)
        require(title.isNotBlank())
        val previous = revisionSnapshot(obj)
        val now = JSONObject().apply {
            put("title", title)
            put("semitones", settings.semitones.coerceIn(-12,12))
            put("cents", settings.cents.coerceIn(-100,100))
            put("speed", settings.speed.coerceIn(0.5,2.0))
            put("quality", settings.quality.name)
            settings.loopA?.let { put("loopA", it.coerceIn(0.0,1.0)) }
            settings.loopB?.let { put("loopB", it.coerceIn(0.0,1.0)) }
            put("position", settings.position.coerceIn(0.0,1.0))
        }
        val important = arrayOf("title","semitones","cents","speed","quality","loopA","loopB")
        val changed = important.any {
            previous.optString(it,"<missing>") != now.optString(it,"<missing>")
        }
        val moved = kotlin.math.abs(previous.optDouble("position",0.0) -
            now.optDouble("position",0.0)) > 0.001
        if (!changed && !moved) return
        if (changed) {
            val oldHistory=obj.optJSONArray("revisionHistory") ?: JSONArray()
            val bounded=JSONArray()
            for (i in (oldHistory.length()-19).coerceAtLeast(0) until oldHistory.length())
                bounded.put(oldHistory.getJSONObject(i))
            previous.put("savedAt", obj.optLong("updatedAt",System.currentTimeMillis()))
            bounded.put(previous)
            obj.put("revisionHistory", bounded)
        }
        for (key in arrayOf("title","semitones","cents","speed","quality","position"))
            obj.put(key,now.get(key))
        for (key in arrayOf("loopA","loopB"))
            if (now.has(key)) obj.put(key,now.get(key)) else obj.remove(key)
        obj.put("updatedAt",System.currentTimeMillis())
        val atomic=AtomicFile(destination)
        var output: FileOutputStream?=null
        try {
            output=atomic.startWrite()
            output.write(obj.toString().toByteArray(Charsets.UTF_8))
            atomic.finishWrite(output)
        } catch (error: Exception) {
            if (output!=null) atomic.failWrite(output)
            throw error
        }
    }

    private fun revisionSnapshot(data: JSONObject): JSONObject = JSONObject().apply {
        for (key in arrayOf("title","semitones","cents","speed","quality",
            "loopA","loopB","position"))
            if (data.has(key)) put(key,data.get(key))
    }

    fun history(context: Context, id: String): List<Revision> {
        val json=JSONObject(metadata(directory(context,id)).readText(Charsets.UTF_8))
        val versions=json.optJSONArray("revisionHistory") ?: return emptyList()
        val title=json.getString("title")
        return (versions.length()-1 downTo 0).mapNotNull { index ->
            try {
                val data=versions.getJSONObject(index)
                val quality=try { DspQuality.valueOf(data.optString("quality","ALTA")) }
                    catch (_: Exception) { DspQuality.ALTA }
                val a=data.optDouble("loopA",Double.NaN)
                    .takeIf{it.isFinite()}?.coerceIn(0.0,1.0)
                val b=data.optDouble("loopB",Double.NaN)
                    .takeIf{it.isFinite()}?.coerceIn(0.0,1.0)
                Revision(data.optLong("savedAt"), Settings(
                    title,data.optInt("semitones",0).coerceIn(-12,12),
                    data.optInt("cents",0).coerceIn(-100,100),
                    data.optDouble("speed",1.0).coerceIn(0.5,2.0),
                    quality,a,b?.takeIf{a!=null&&it>a},
                    data.optDouble("position",0.0).coerceIn(0.0,1.0)
                ))
            } catch (_: Exception) { null }
        }
    }

'''
l=change(l,"    fun open(context: Context, id: String): Opened {\n",
         addlib+"    fun open(context: Context, id: String): Opened {\n")
s=change(s,"    private var libraryOpenGeneration = 0",
"""    private var libraryOpenGeneration = 0
    private var activeProjectId: String? = null
    private var activeProjectTitle: String? = null
    private val librarySaveRunnable = Runnable { flushLibraryAutosave() }""")
s=change(s,"        saveEditorPreferences()\n",
         "        saveEditorPreferences()\n        flushLibraryAutosave()\n")
s=change(s,"            onSeek = { player.seekFraction(it) }",
         "            onSeek = { player.seekFraction(it); scheduleLibraryAutosave() }")
s=change(s,"        if (immediate) startProcess(source, generation) else handler.postDelayed(processRunnable, 260)",
"""        if (immediate) startProcess(source, generation) else handler.postDelayed(processRunnable, 260)
        scheduleLibraryAutosave()""")
s=change(s,"        applyLoop()\n    }\n    private fun markB()",
         "        applyLoop(); scheduleLibraryAutosave()\n    }\n    private fun markB()")
s=change(s,"        applyLoop()\n    }\n    private fun clearLoop()",
         "        applyLoop(); scheduleLibraryAutosave()\n    }\n    private fun clearLoop()")
s=change(s,"    private fun clearLoop() { loopA = null; loopB = null; applyLoop() }",
         "    private fun clearLoop() { loopA = null; loopB = null; applyLoop(); scheduleLibraryAutosave() }")
addedMain=r'''    /** Atualizações de ajustes são locais e não duplicam o arquivo de áudio. */
    private fun scheduleLibraryAutosave() {
        if (activeProjectId == null || original == null) return
        handler.removeCallbacks(librarySaveRunnable)
        handler.postDelayed(librarySaveRunnable, 1500L)
    }

    private fun flushLibraryAutosave() {
        handler.removeCallbacks(librarySaveRunnable)
        val id = activeProjectId ?: return
        val source = original ?: return
        try {
            ProjectLibrary.updateSettings(this,id,ProjectLibrary.Settings(
                activeProjectTitle ?: source.name, semitones,cents,speed,
                quality,loopA,loopB,player.fraction()
            ))
        } catch (error: Exception) {
            android.util.Log.w("BEATflow-Library","Autosave falhou",error)
            if (!isFinishing && !isDestroyed)
                toast("Não foi possível salvar automaticamente os ajustes.")
        }
    }

    private fun showProjectHistory(entry: ProjectLibrary.Entry) {
        val history=try { ProjectLibrary.history(this,entry.id) }
                    catch (_: Exception) { emptyList() }
        if (history.isEmpty()) {
            MaterialAlertDialogBuilder(this).setTitle("Histórico de ajustes")
                .setMessage("Nenhuma versão anterior disponível. O histórico começa após alterar os ajustes de um projeto salvo.")
                .setPositiveButton("Entendi",null).show()
            return
        }
        val fmt=DateFormat.getDateTimeInstance(DateFormat.SHORT,DateFormat.SHORT)
        val labels=history.map { rev ->
            val r=rev.settings
            fmt.format(Date(rev.savedAt)) + " · Tom " +
                (if(r.semitones>0) "+" else "") + r.semitones +
                " · " + String.format(java.util.Locale("pt","BR"),"%.2fx",r.speed)
        }.toTypedArray()
        MaterialAlertDialogBuilder(this).setTitle("Histórico: "+entry.title)
            .setItems(labels) { _, index ->
                val snapshot=history[index]
                MaterialAlertDialogBuilder(this)
                    .setTitle("Restaurar ajustes anteriores?")
                    .setMessage("O áudio original será preservado. Os ajustes atuais poderão ser recuperados pelo histórico.")
                    .setNegativeButton("Cancelar",null)
                    .setPositiveButton("Restaurar") { _, _ ->
                        flushLibraryAutosave()
                        activeProjectId = null
                        try {
                            ProjectLibrary.updateSettings(this,entry.id,snapshot.settings)
                            openSavedProject(entry)
                        } catch (error: Exception) {
                            toast("Falha ao restaurar ajustes: "+error.message)
                        }
                    }.show()
            }.setNegativeButton("Voltar") { _, _ -> showProjectActions(entry) }
            .show()
    }

'''
s=change(s,"    private fun promptSaveProject() {\n",addedMain+"    private fun promptSaveProject() {\n")
s=change(s,"""                                hideProgress("Projeto salvo: " + entry.title)
                                toast("Projeto salvo.")""",
"""                                hideProgress("Projeto salvo: " + entry.title)
                                if (original === source) {
                                    activeProjectId=entry.id
                                    activeProjectTitle=entry.title
                                    scheduleLibraryAutosave()
                                }
                                toast("Projeto salvo.")""")
s=change(s,"""            .setItems(arrayOf("Abrir e continuar", "Excluir projeto")) { _, selection ->
                if (selection == 0) openSavedProject(entry) else confirmDeleteProject(entry)
            }""",
"""            .setItems(arrayOf("Abrir e continuar","Histórico de ajustes","Excluir projeto")) { _, selection ->
                when (selection) {
                    0 -> openSavedProject(entry)
                    1 -> showProjectHistory(entry)
                    else -> confirmDeleteProject(entry)
                }
            }""")
s=change(s,"""                    original = project
                    processed = null
                    keyEstimate = estimate""",
"""                    original = project
                    activeProjectId = entry.id
                    activeProjectTitle = settings.title
                    processed = null
                    keyEstimate = estimate""")
s=change(s,"""    private fun cleanupProjects() {
        ++processingGeneration""",
"""    private fun cleanupProjects() {
        flushLibraryAutosave()
        activeProjectId = null
        activeProjectTitle = null
        ++processingGeneration""")
assert "YouTubeBrowserActivity.EXTRA_FILE_PATH" in s
assert "AtomicFile(destination)" in l
assert "revisionHistory" in l
assert "Histórico de ajustes" in s
lib.write_text(l,encoding="utf-8")
main.write_text(s,encoding="utf-8")
gradle=root/"app/build.gradle.kts"
g=gradle.read_text(encoding="utf-8")
for before,after in (
 ("versionCode = 34","versionCode = 35"),
 ('versionName = "1.12.3"','versionName = "1.12.4"')
):
 if g.count(before)!=1: raise SystemExit("Base 1.12.3 incompatível: "+before)
 g=g.replace(before,after,1)
gradle.write_text(g,encoding="utf-8")
print("BEAT flow v1.12.4: autosave e histórico de ajustes integrados.")

#!/usr/bin/env python3
"""BEAT flow 1.13.5: rolagem autônoma das letras e controles de ensaio.
Apenas StageActivity, versionCode e novo helper StageRehearsalMath.
"""
from pathlib import Path
import sys
root=Path(sys.argv[1]).resolve()
src=root/"app/src/main/java/br/com/timachado/pitchstudio/StageActivity.kt"
s=src.read_text(encoding="utf-8")
def replace(old,new):
    global s
    if s.count(old)!=1:
        raise RuntimeError(f"Base StageActivity divergente ({s.count(old)}): {old[:100]}")
    s=s.replace(old,new,1)

replace("    private var stageMode = false\n",'''    private var stageMode = false
    private var lyricsAutoScroll = false
    private var lyricsSpeed = 1 // 0 lento, 1 médio, 2 rápido
    private lateinit var rootScroll: ScrollView
    private lateinit var lyricsScroll: ScrollView
    private lateinit var scrollButton: MaterialButton
    private lateinit var speedButton: MaterialButton
''')
replace("    private val progressTick = object : Runnable {",'''    // A rolagem é visual: não modifica pitch, velocidade nem posição do áudio.
    private val lyricsTick = object : Runnable {
        override fun run() {
            if (!lyricsAutoScroll || isFinishing || isDestroyed) return
            if (::lyricsScroll.isInitialized) {
                val child = lyricsScroll.getChildAt(0) ?: return
                val limit = (child.height - lyricsScroll.height).coerceAtLeast(0)
                if (lyricsScroll.scrollY >= limit) {
                    stopLyricsScroll(false)
                    return
                }
                lyricsScroll.scrollBy(
                    0, StageRehearsalMath.scrollPixels(lyricsSpeed, resources.displayMetrics.density)
                )
                handler.postDelayed(this, 100L)
            }
        }
    }

    private val progressTick = object : Runnable {''')
replace('''    override fun onPause() {
        super.onPause()
        player.pause()
        refreshTransport()
    }''','''    override fun onPause() {
        super.onPause()
        stopLyricsScroll(false)
        player.pause()
        refreshTransport()
    }''')
replace('''        val scroll=ScrollView(this).apply {isFillViewport=true;addView(column)}
        setContentView(scroll)''','''        rootScroll=ScrollView(this).apply {isFillViewport=true;addView(column)}
        setContentView(rootScroll)''')
replace('''        column.addView(transport,full(top=6))
        status=text(''','''        column.addView(transport,full(top=6))
        val navigation=row()
        rowBtn(navigation,"◀ 10 s") { seekBy(-10.0) }
        rowBtn(navigation,"10 s ▶") { seekBy(10.0) }
        rowBtn(navigation,"Ver letra ↓") {
            rootScroll.post { rootScroll.smoothScrollTo(0,lyricsScroll.top) }
        }
        column.addView(navigation,full(top=4))
        val loopButtons=row()
        rowBtn(loopButtons,"Marcar A") { markLoopStart() }
        rowBtn(loopButtons,"Marcar B") { markLoopEnd() }
        rowBtn(loopButtons,"Limpar A/B") { clearLoop() }
        column.addView(loopButtons,full(top=4))
        status=text(''')
replace('''        column.addView(lyricButtons,full(top=7))
        lyrics=text(''','''        column.addView(lyricButtons,full(top=7))
        val lyricControls=row()
        scrollButton=btn("▶ Rolar letra") { toggleLyricsScroll() }
        lyricControls.addView(scrollButton,LinearLayout.LayoutParams(0,dp(51),1f))
        speedButton=btn("Velocidade: Média") { cycleLyricsSpeed() }
        lyricControls.addView(speedButton,LinearLayout.LayoutParams(0,dp(51),1f))
        column.addView(lyricControls,full(top=6))
        column.addView(btn("↑ Voltar ao topo da letra") {
            stopLyricsScroll(false)
            lyricsScroll.smoothScrollTo(0,0)
        },full(dp(45),top=4))
        lyrics=text(''')
replace('''        column.addView(lyrics,full(top=10))
        column.addView(text("Músicas do repertório"''','''        lyricsScroll=ScrollView(this).apply {
            isFillViewport=false
            addView(lyrics,android.widget.FrameLayout.LayoutParams(-1,-2))
            contentDescription="Letra da música com rolagem manual ou automática"
        }
        column.addView(lyricsScroll,full(dp(270),top=10))
        column.addView(text("Músicas do repertório"''')
replace('''    private fun save(set:StageSetlists.Setlist) {StageSetlists.update(this,set);updateUi()}''','''    // Controles locais de palco/ensaio: nenhuma alteração em projetos ou áudio.
    private fun stopLyricsScroll(reset:Boolean) {
        lyricsAutoScroll=false
        handler.removeCallbacks(lyricsTick)
        if (::scrollButton.isInitialized) scrollButton.text="▶ Rolar letra"
        if (reset && ::lyricsScroll.isInitialized)
            lyricsScroll.post { lyricsScroll.scrollTo(0,0) }
    }
    private fun toggleLyricsScroll() {
        if (lyricsAutoScroll) stopLyricsScroll(false) else {
            lyricsAutoScroll=true
            scrollButton.text="Ⅱ Parar rolagem"
            handler.post(lyricsTick)
        }
    }
    private fun cycleLyricsSpeed() {
        lyricsSpeed=(lyricsSpeed+1)%3
        speedButton.text="Velocidade: "+listOf("Lenta","Média","Rápida")[lyricsSpeed]
    }
    private fun seekBy(seconds:Double) {
        val p=player.project ?: return
        player.seekFraction(StageRehearsalMath.seek(
            player.fraction(), seconds, p.frames, p.sampleRate))
    }
    private fun markLoopStart() {
        if (stageMode) {
            status.text="Repetição A/B disponível no Modo Ensaio."
            return
        }
        if (player.project==null)return
        val at=player.fraction()
        player.loopA=at
        if ((player.loopB ?: 0.0)<=at) player.loopB=null
        status.text="A marcado em "+clock(at*songDuration())
    }
    private fun markLoopEnd() {
        if (stageMode) {
            status.text="Repetição A/B disponível no Modo Ensaio."
            return
        }
        if (player.project==null)return
        val at=player.fraction()
        if (!StageRehearsalMath.validLoop(player.loopA,at)) {
            status.text="Marque A e depois B em um ponto posterior."
            return
        }
        player.loopB=at
        status.text="Repetição A/B ativa · "+clock(player.loopA!!*songDuration())+
            " a "+clock(at*songDuration())
    }
    private fun clearLoop() {
        player.loopA=null
        player.loopB=null
        status.text="Repetição A/B desativada."
    }
    private fun songDuration():Double =
        player.project?.let {it.frames.toDouble()/it.sampleRate} ?: 0.0

    private fun save(set:StageSetlists.Setlist) {StageSetlists.update(this,set);updateUi()}''')
replace('''    private fun load(index:Int,autoPlay:Boolean) {
        val set=current() ?: return''','''    private fun load(index:Int,autoPlay:Boolean) {
        val set=current() ?: return
        stopLyricsScroll(true)''')
replace('''        lyrics.textSize=if(stageMode) 27f else 21f
        trackList.removeAllViews()''','''        lyrics.textSize=if(stageMode) 27f else 21f
        lyricsScroll.layoutParams?.let {
            it.height=dp(if(stageMode) 440 else 270)
            lyricsScroll.layoutParams=it
        }
        trackList.removeAllViews()''')
replace('''    private fun toggleMode() {
        stageMode=!stageMode''','''    private fun toggleMode() {
        stopLyricsScroll(false)
        stageMode=!stageMode''')
# Evita estado antigo da prévia de palco ao trocar repertório.
replace('''                player.pause();player.setProject(null)
                setlistId=items[which].id''','''                stopLyricsScroll(true)
                player.pause();player.setProject(null)
                setlistId=items[which].id''')
src.write_text(s,encoding="utf-8")
gradle=root/"app/build.gradle.kts"
g=gradle.read_text(encoding="utf-8")
for old,new in [("versionCode = 45","versionCode = 46"),
                ('versionName = "1.13.4"','versionName = "1.13.5"')]:
    if g.count(old)!=1:raise RuntimeError("Versão-base diferente: "+old)
    g=g.replace(old,new,1)
gradle.write_text(g,encoding="utf-8")
print("BEAT flow v1.13.5: letra rolável, controle de velocidade, navegação +/-10s e A/B de ensaio.")

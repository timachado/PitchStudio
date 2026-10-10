#!/usr/bin/env python3
"""BEAT flow v1.13.13: connect saved library projects to Stage repertoires explicitly."""
from pathlib import Path
import sys

root=Path(sys.argv[1]).resolve()
src=root/"app/src/main/java/br/com/timachado/pitchstudio"
stage=src/"StageActivity.kt"
main=src/"MainActivity.kt"
gradle=root/"app/build.gradle.kts"
s=stage.read_text(encoding="utf-8")

def replace(old,new):
    global s
    assert s.count(old)==1, f"Stage changed unexpectedly ({s.count(old)}): {old[:90]!r}"
    s=s.replace(old,new,1)

replace('''    private lateinit var setlistTitle: TextView
    private lateinit var track: TextView''','''    private lateinit var setlistTitle: TextView
    private lateinit var libraryNotice: TextView
    private lateinit var track: TextView''')

replace('''        buildUi()
        updateUi()
        handler.post(progressTick)''','''        buildUi()
        updateUi()
        offerLibraryImportIfEmpty()
        handler.post(progressTick)''')

replace('''        column.addView(setlistTitle,full(top=17))
        val lists=row()''','''        column.addView(setlistTitle,full(top=17))
        libraryNotice=text("",13f)
        column.addView(libraryNotice,full(top=3))
        val lists=row()''')

replace('''        val set=current()
        val names=ProjectLibrary.list(this).associateBy {it.id}
        if(set==null)''','''        val set=current()
        val names=ProjectLibrary.list(this).associateBy {it.id}
        val pending=names.keys.count { id -> set?.songIds?.contains(id) != true }
        libraryNotice.text=when {
            set==null -> "Escolha ou crie um repertório para adicionar músicas salvas."
            pending>0 -> pending.toString() + " música(s) salva(s) na Biblioteca aguardando inclusão. Toque em Adicionar música."
            set.songIds.isEmpty() -> "Este repertório está vazio. Salve uma música na Biblioteca primeiro."
            else -> "Toque em uma música da lista abaixo para carregar os controles do ensaio."
        }
        if(set==null)''')

replace('''        refreshTransport()
        if (::harmonyStatus.isInitialized) refreshHarmony()''','''        playBtn.isEnabled=player.project!=null
        progress.isEnabled=player.project!=null
        refreshTransport()
        if (::harmonyStatus.isInitialized) refreshHarmony()''')

replace('''    private fun addSong() {
        val set=current() ?: run {chooseSetlist();return}
        val available=ProjectLibrary.list(this).filterNot {it.id in set.songIds}
        if(available.isEmpty()) {
            Toast.makeText(this,"Salve um projeto na Biblioteca Inteligente primeiro.",Toast.LENGTH_LONG).show()
            return
        }
        MaterialAlertDialogBuilder(this).setTitle("Adicionar projeto salvo")
            .setItems(available.map {it.title}.toTypedArray()) {_,index ->
                save(set.copy(songIds=StageSetlistOrder.add(set.songIds,available[index].id)))
            }.setNegativeButton("Cancelar",null).show()
    }''','''    private fun offerLibraryImportIfEmpty() {
        val set=current() ?: return
        if(set.songIds.isNotEmpty()) return
        val available=ProjectLibrary.list(this)
        if(available.isEmpty()) return
        val key="stage_library_offer_"+set.id
        val prefs=getPreferences(MODE_PRIVATE)
        // Perguntar uma vez para cada quantidade nova de projetos. Nunca
        // acrescentar repertórios silenciosamente nem duplicar áudio PCM.
        if(prefs.getInt(key,-1)==available.size) return
        prefs.edit().putInt(key,available.size).apply()
        rootScroll.post {
            if(isFinishing || isDestroyed || current()?.id!=set.id) return@post
            MaterialAlertDialogBuilder(this)
                .setTitle("Músicas encontradas na Biblioteca")
                .setMessage(available.size.toString()+" projeto(s) salvo(s). Deseja incluí-los no repertório "+
                    set.title+"? O áudio original não será copiado.")
                .setPositiveButton("Escolher música") {_,_-> addSong() }
                .setNeutralButton("Adicionar todas") {_,_->
                    try {
                        val ids=available.take(StageSetlistOrder.MAX_SONGS)
                            .fold(set.songIds) { acc, song ->
                                StageSetlistOrder.add(acc,song.id)
                            }
                        StageSetlists.update(this,set.copy(songIds=ids))
                        load(0,false)
                        status.text="Músicas incluídas. Escolha Reproduzir para iniciar."
                        rootScroll.post {rootScroll.smoothScrollTo(0,0)}
                    } catch(e:Exception) { report(e) }
                }
                .setNegativeButton("Agora não",null)
                .show()
        }
    }

    private fun addSong() {
        val set=current() ?: run {chooseSetlist();return}
        val savedProjects=ProjectLibrary.list(this)
        val available=savedProjects.filterNot { it.id in set.songIds }
        if(available.isEmpty()) {
            val message=if(savedProjects.isEmpty())
                "Biblioteca vazia. Importe uma música no Estúdio e toque em Salvar projeto."
                else "Todas as músicas da Biblioteca já estão neste repertório."
            Toast.makeText(this,message,Toast.LENGTH_LONG).show()
            return
        }
        MaterialAlertDialogBuilder(this)
            .setTitle("Adicionar da Biblioteca Inteligente")
            .setItems(available.map {it.title}.toTypedArray()) {_,index ->
                val selected=available[index]
                try {
                    val ids=StageSetlistOrder.add(set.songIds,selected.id)
                    StageSetlists.update(this,set.copy(songIds=ids))
                    // Antes o repertório ficava com 1 música mas selectedIndex=-1:
                    // o usuário tocava Reproduzir e nada acontecia.
                    load(ids.indexOf(selected.id),false)
                    status.text="Música adicionada e selecionada: "+selected.title
                    rootScroll.post {rootScroll.smoothScrollTo(0,0)}
                } catch(e:Exception) { report(e) }
            }.setNegativeButton("Cancelar",null).show()
    }''')

stage.write_text(s,encoding="utf-8")
m=main.read_text(encoding="utf-8")
old='''                                toast("Projeto salvo.")'''
new='''                                toast("Projeto salvo. No Modo Palco, toque em Adicionar música para incluí-lo no repertório.")'''
assert m.count(old)==1, "Unexpected post-save toast"
main.write_text(m.replace(old,new,1),encoding="utf-8")
g=gradle.read_text(encoding="utf-8")
for old,new in [('versionCode = 53','versionCode = 54'),
                ('versionName = "1.13.12"','versionName = "1.13.13"')]:
    assert g.count(old)==1,"Unexpected Gradle version: "+old
    g=g.replace(old,new,1)
gradle.write_text(g,encoding="utf-8")
print("PASSOU: inclusão explícita, seleção imediata, ajuda contextual e versão 1.13.13.")

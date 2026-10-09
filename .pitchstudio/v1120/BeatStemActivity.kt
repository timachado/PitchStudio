package br.com.timachado.pitchstudio

import android.app.Activity
import android.content.Intent
import android.content.res.ColorStateList
import android.graphics.Color
import android.os.Bundle
import android.view.View
import android.widget.LinearLayout
import android.widget.ProgressBar
import android.widget.ScrollView
import android.widget.TextView
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat
import br.com.timachado.pitchstudio.audio.AudioProject
import br.com.timachado.pitchstudio.audio.Mp3Exporter
import br.com.timachado.pitchstudio.audio.PcmAudioPlayer
import com.google.android.material.button.MaterialButton
import com.google.android.material.card.MaterialCardView
import java.io.File
import java.io.FileInputStream
import java.io.InterruptedIOException

class BeatStemActivity : Activity() {
    companion object {
        const val FILE="beat_file"
        const val RATE="beat_rate"
        const val CHANNELS="beat_channels"
        const val FRAMES="beat_frames"
        const val FRACTION="beat_fraction"
        const val NAME="beat_name"
        private const val SAVE=9501
    }
    private val bg=Color.rgb(13,16,32)
    private val lime=Color.rgb(200,255,112)
    private val cyan=Color.rgb(23,213,226)
    private val surface=Color.rgb(25,28,50)
    private val ink=Color.WHITE
    private var original:AudioProject?=null
    private var result:VocalStemSeparator.Stems?=null
    private var mode=VocalStemSeparator.StemMode.PLAYBACK
    private var entire=true
    private var duration=18
    private var voiceSelected=false
    @Volatile private var worker:Thread?=null
    private var saving=false
    private var exportMp3=false
    private var exportClip:AudioProject?=null
    private lateinit var message:TextView
    private lateinit var bar:ProgressBar
    private lateinit var start:MaterialButton
    private lateinit var cancel:MaterialButton
    private lateinit var preview:MaterialButton
    private lateinit var choose:MaterialButton
    private lateinit var wav:MaterialButton
    private lateinit var mp3:MaterialButton
    private lateinit var modes:LinearLayout
    private lateinit var scopes:LinearLayout
    private lateinit var durations:LinearLayout
    private val player=PcmAudioPlayer { runOnUiThread {
        if(::preview.isInitialized)preview.text="▶ Ouvir prévia"
    } }
    private fun dp(x:Int)=(x*resources.displayMetrics.density).toInt()
    private fun caption(s:String,size:Float=15f)=TextView(this).apply{
        text=s;textSize=size;setTextColor(ink)
    }
    private fun btn(s:String,highlight:Boolean=false,click:()->Unit)=MaterialButton(this).apply{
        text=s;isAllCaps=false;cornerRadius=dp(22);minHeight=dp(52)
        backgroundTintList=ColorStateList.valueOf(if(highlight)lime else surface)
        setTextColor(if(highlight)bg else ink)
        setOnClickListener{click()}
    }
    private fun add(col:LinearLayout,v:View,spacing:Int=10) {
        col.addView(v,LinearLayout.LayoutParams(-1,-2).apply{topMargin=dp(spacing)})
    }
    private fun card(parent:LinearLayout,title:String):LinearLayout{
        val shell=MaterialCardView(this).apply{
            radius=dp(25).toFloat();strokeWidth=dp(1)
            strokeColor=Color.rgb(52,64,95)
            setCardBackgroundColor(surface)
        }
        val body=LinearLayout(this).apply{
            orientation=LinearLayout.VERTICAL
            setPadding(dp(16),dp(16),dp(16),dp(17))
        }
        add(body,caption(title,19f),0);shell.addView(body);add(parent,shell,16)
        return body
    }
    private fun row()=LinearLayout(this).apply{orientation=LinearLayout.HORIZONTAL}
    private fun cell(row:LinearLayout,v:MaterialButton){
        row.addView(v,LinearLayout.LayoutParams(0,dp(56),1f).apply{
            setMargins(dp(2),0,dp(2),0)
        })
    }
    override fun onCreate(state:Bundle?){
        super.onCreate(state)
        window.statusBarColor=bg;window.navigationBarColor=bg
        val file=File(intent.getStringExtra(FILE)?:"")
        val rate=intent.getIntExtra(RATE,0)
        val chans=intent.getIntExtra(CHANNELS,0)
        val frames=intent.getLongExtra(FRAMES,0)
        val valid=try{
            (file.canonicalPath.startsWith(cacheDir.canonicalPath+File.separator)
                || file.canonicalPath.startsWith(filesDir.canonicalPath+File.separator))
                && file.isFile && rate in 8000..192000 && chans in 1..2 && frames>0L
                && frames<Long.MAX_VALUE/(chans*4L)
                && file.length()==frames*chans*4L
        }catch(_:Exception){false}
        if(valid)original=AudioProject(intent.getStringExtra(NAME)?:"Música importada",
            file,rate,chans,frames,0f,floatArrayOf(0f))
        val scroll=ScrollView(this).apply{setBackgroundColor(bg)}
        ViewCompat.setOnApplyWindowInsetsListener(scroll){v,i->
            val b=i.getInsets(WindowInsetsCompat.Type.systemBars())
            v.setPadding(dp(15)+b.left,dp(8)+b.top,dp(15)+b.right,dp(24)+b.bottom)
            i
        }
        val root=LinearLayout(this).apply{orientation=LinearLayout.VERTICAL}
        scroll.addView(root)
        add(root,btn("‹    BEAT flow"){finish()},0)
        add(root,caption("FERRAMENTAS DE IA",13f),16)
        add(root,caption("Separação com IA",29f),5)
        add(root,caption("Isole a voz, gere playback ou salve os dois arquivos."),9)
        val track=card(root,"Música selecionada")
        add(track,caption(original?.name?:"Importe uma música no editor."),8)
        if(original!=null)add(track,caption(
            "%.1f segundos • processamento local".format(original!!.durationSeconds),13f),5)
        val controls=card(root,"O que você quer separar?")
        modes=row();add(controls,modes)
        add(controls,caption("Alcance do processamento",17f),18)
        scopes=row();add(controls,scopes)
        durations=row();add(controls,durations)
        renderModes()
        start=btn("✦ Processar música inteira",true){process()}
        start.isEnabled=original!=null;add(controls,start,16)
        cancel=btn("Cancelar processamento"){worker?.interrupt()
            cancel.isEnabled=false;message.text="Cancelando e limpando os arquivos…"}
        cancel.isEnabled=false;add(controls,cancel)
        val output=card(root,"Prévia do resultado")
        message=caption("Pronto para separar.",15f);add(output,message)
        bar=ProgressBar(this,null,android.R.attr.progressBarStyleHorizontal).apply{
            max=100
            progressTintList=ColorStateList.valueOf(cyan)
        }
        add(output,bar)
        choose=btn("Resultado: Playback"){changeStem()}
        choose.isEnabled=false;add(output,choose)
        preview=btn("▶ Ouvir prévia"){player.toggle()
            preview.text=if(player.isPlaying())"❚❚ Pausar" else "▶ Ouvir prévia"}
        preview.isEnabled=false;add(output,preview)
        wav=btn("↓ Salvar WAV"){beginSave(false)}
        mp3=btn("↓ Salvar MP3 (320 kbps)"){beginSave(true)}
        wav.isEnabled=false;mp3.isEnabled=false
        add(output,wav);add(output,mp3)
        add(root,caption("Áudio no próprio aparelho. A remoção vocal pode deixar artefatos dependendo da mixagem.",12f),16)
        setContentView(scroll);ViewCompat.requestApplyInsets(scroll)
    }
    private fun renderModes(){
        modes.removeAllViews()
        for((name,value) in listOf(
            "Voz" to VocalStemSeparator.StemMode.VOICE,
            "Playback" to VocalStemSeparator.StemMode.PLAYBACK,
            "Ambos" to VocalStemSeparator.StemMode.BOTH
        ))cell(modes,btn(name,mode==value){mode=value;renderModes()})
        scopes.removeAllViews()
        cell(scopes,btn("Prévia",!entire){entire=false;renderModes()})
        cell(scopes,btn("Música inteira",entire){entire=true;renderModes()})
        durations.removeAllViews()
        durations.visibility=if(entire)View.GONE else View.VISIBLE
        if(!entire)for(n in listOf(6,12,18))
            cell(durations,btn(n.toString()+" s",duration==n){duration=n;renderModes()})
        if(::start.isInitialized)
            start.text=if(entire)"✦ Processar música inteira"
                else "✦ Processar prévia "+duration+" s"
    }
    private fun selected()=if(voiceSelected)result?.vocals else result?.playback
    private fun clearResults(){
        player.pause();player.setProject(null)
        result?.vocals?.pcmFile?.delete()
        result?.playback?.pcmFile?.delete()
        result=null
    }
    private fun changeStem(){
        if(result?.vocals==null || result?.playback==null)return
        voiceSelected=!voiceSelected
        player.pause();player.setProject(selected())
        choose.text=if(voiceSelected)"Resultado: Voz" else "Resultado: Playback"
        preview.text="▶ Ouvir prévia"
    }
    private fun ready(){
        voiceSelected=result?.playback==null
        val clip=selected()
        player.setProject(clip)
        choose.isEnabled=result?.vocals!=null && result?.playback!=null
        preview.isEnabled=clip!=null;wav.isEnabled=clip!=null;mp3.isEnabled=clip!=null
        choose.text=if(voiceSelected)"Resultado: Voz" else "Resultado: Playback"
        message.text=if(clip==null)"Nenhum resultado"
            else "Processado: %.1f s • %s".format(clip.durationSeconds,
                if(clip.channels==2)"estéreo" else "mono")
    }
    private fun process(){
        if(worker?.isAlive==true || saving)return
        val source=original?:return
        clearResults()
        val requestedMode=mode
        val clipSeconds=if(entire)null else duration
        val fraction=intent.getDoubleExtra(FRACTION,0.0)
        start.isEnabled=false;cancel.isEnabled=true
        preview.isEnabled=false;wav.isEnabled=false;mp3.isEnabled=false
        choose.isEnabled=false
        bar.progress=0;message.text="Processando com IA…"
        val thread=Thread({
            try{
                val output=VocalStemSeparator.separateStems(
                    this,source,requestedMode,clipSeconds,fraction
                ){value->runOnUiThread{
                    if(!isDestroyed && !isFinishing){
                        bar.progress=value;message.text="Separando áudio: "+value+"%"
                    }
                }}
                runOnUiThread{
                    if(isDestroyed || isFinishing){
                        output.vocals?.pcmFile?.delete()
                        output.playback?.pcmFile?.delete()
                    }else{result=output;ready()}
                }
            }catch(e:Throwable){
                runOnUiThread{if(!isDestroyed){
                    message.text=if(e is InterruptedIOException)
                        "Processamento cancelado." else "Falha: "+(e.message?:"erro de IA")
                }}
            }finally{
                runOnUiThread{if(!isDestroyed){
                    start.isEnabled=true;cancel.isEnabled=false
                }}
            }
        },"BEATflow-Separation")
        worker=thread;thread.start()
    }
    private fun beginSave(isMp3:Boolean){
        if(saving || worker?.isAlive==true)return
        val clip=selected()?:return
        exportClip=clip;exportMp3=isMp3
        val ext=if(isMp3)"mp3" else "wav"
        val title="BEATflow_"+(if(voiceSelected)"Voz" else "Playback")+"."+ext
        try{
            startActivityForResult(Intent(Intent.ACTION_CREATE_DOCUMENT).apply{
                addCategory(Intent.CATEGORY_OPENABLE)
                type=if(isMp3)"audio/mpeg" else "audio/wav"
                putExtra(Intent.EXTRA_TITLE,title)
            },SAVE)
        }catch(e:Exception){message.text="Não foi possível abrir o seletor de arquivos."}
    }
    @Deprecated("Android SAF")
    override fun onActivityResult(requestCode:Int,resultCode:Int,data:Intent?){
        super.onActivityResult(requestCode,resultCode,data)
        if(requestCode!=SAVE)return
        val uri=data?.data
        val clip=exportClip
        if(resultCode!=RESULT_OK || uri==null || clip==null){
            message.text="Salvamento cancelado.";return
        }
        saving=true;wav.isEnabled=false;mp3.isEnabled=false
        message.text="Exportando para o dispositivo…"
        val isMp3=exportMp3
        Thread({
            var temporary:File?=null
            try{
                if(isMp3){
                    val sink=requireNotNull(contentResolver.openOutputStream(uri,"w"))
                    sink.use{out->FileInputStream(clip.pcmFile).use{input->
                        Mp3Exporter.export320(clip,input,out)
                    }}
                }else{
                    temporary=File.createTempFile("beat_export_",".wav",cacheDir)
                    StemWavExporter.exportToFile(clip.pcmFile,clip.sampleRate,
                        clip.channels,clip.frames,temporary)
                    val sink=requireNotNull(contentResolver.openOutputStream(uri,"w"))
                    sink.use{out->FileInputStream(temporary).use{input->
                        input.copyTo(out,64*1024)
                    }}
                }
                runOnUiThread{if(!isDestroyed)message.text="Arquivo salvo no local escolhido."}
            }catch(e:Throwable){
                runOnUiThread{if(!isDestroyed)
                    message.text="Erro ao exportar: "+(e.message?:"destino indisponível")}
            }finally{
                temporary?.delete()
                runOnUiThread{
                    saving=false
                    if(!isDestroyed){wav.isEnabled=selected()!=null;mp3.isEnabled=selected()!=null}
                }
            }
        },"BEATflow-Export").start()
    }
    override fun onStop(){player.pause();super.onStop()}
    override fun onDestroy(){
        worker?.interrupt()
        player.release()
        val previous=worker
        if(previous?.isAlive==true)Thread{
            try{previous.join()}catch(_:InterruptedException){}
            clearResults()
        }.start()else clearResults()
        super.onDestroy()
    }
}

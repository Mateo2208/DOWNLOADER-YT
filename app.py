from flask import Flask, request, render_template, send_from_directory
from pytube import YouTube
import os
import subprocess
import re

app = Flask(__name__)
app.config['DOWNLOAD_FOLDER'] = 'downloads'

def clean_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', "", filename)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/Downloads', methods=['POST'])
def descargar():
    url = request.form['url']
    download_format = request.form['format']
    
    try:
        yt = YouTube(url)
        
        # Especificar la carpeta de destino
        download_path = app.config['DOWNLOAD_FOLDER']
        
        # Crear la carpeta si no existe
        if not os.path.exists(download_path):
            os.makedirs(download_path)
        
        if download_format == 'video':
            # Obtener el stream de video de mayor resolución
            video_stream = yt.streams.filter(progressive=False, file_extension='mp4').order_by('resolution').desc().first()
            
            # Descargar el video
            video_file = video_stream.download(output_path=download_path)
            filename = os.path.basename(video_file)
            
            return render_template('result.html', title=yt.title, download_path=filename)
        
        elif download_format == 'audio':
            # Obtener el stream de audio de mayor calidad
            audio_stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
            
            # Descargar el audio
            audio_file = audio_stream.download(output_path=download_path, filename='audio.mp4')
            
            # Renombrar el archivo de audio a .mp3
            base, ext = os.path.splitext(audio_file)
            new_file = base + '.mp3'
            os.rename(audio_file, new_file)
            filename = os.path.basename(new_file)
            
            return render_template('result.html', title=yt.title, download_path=filename)
        
        elif download_format == 'both':
            # Obtener el stream de video de mayor resolución
            video_stream = yt.streams.filter(progressive=False, file_extension='mp4').order_by('resolution').desc().first()
            
            # Obtener el stream de audio de mayor calidad
            audio_stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
            
            # Descargar los streams
            video_file = video_stream.download(output_path=download_path, filename='video.mp4')
            audio_file = audio_stream.download(output_path=download_path, filename='audio.mp4')
            
            # Limpiar el nombre del archivo de salida
            output_filename = clean_filename(yt.title) + ".mp4"
            output_path = os.path.join(download_path, output_filename)
            
            # Usar ffmpeg para combinar los streams de video y audio
            ffmpeg_command = [
                'ffmpeg', '-i', video_file, '-i', audio_file, '-c:v', 'copy', '-c:a', 'aac', '-strict', 'experimental', output_path
            ]
            
            # Ejecutar el comando ffmpeg y capturar la salida en bytes
            result = subprocess.run(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Decodificar la salida
            stdout = result.stdout.decode('utf-8', errors='replace')
            stderr = result.stderr.decode('utf-8', errors='replace')
            
            # Verificar si ffmpeg tuvo éxito
            if result.returncode != 0:
                error_message = f"ffmpeg error: {stderr}"
                return f'Ha ocurrido un error: {error_message}'
            
            # Eliminar los archivos temporales
            os.remove(video_file)
            os.remove(audio_file)
            filename = os.path.basename(output_path)
            
            return render_template('result.html', title=yt.title, download_path=filename)
        
    except Exception as e:
        return render_template('result.html', error=str(e))

@app.route('/downloads/<path:filename>')
def download_file(filename):
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import sys
import os


def install_packages():
    required_packages = ['pytube', 'pydub']
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            __import__(package)


def check_ffmpeg_installed():
    try:
        subprocess.run(["ffmpeg", "-version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def install_ffmpeg():
    try:
        messagebox.showinfo(translations['FFmpeg Installation'][current_lang],
                            translations['Installing FFmpeg'][current_lang])
        subprocess.run(["winget", "install", "--id=Gyan.FFmpeg", "--source=winget"], check=True)
        messagebox.showinfo(translations['FFmpeg Installation'][current_lang],
                            translations['FFmpeg Installed'][current_lang])
        return True
    except subprocess.CalledProcessError as e:
        messagebox.showerror(translations['Installation Failed'][current_lang],
                             f"{translations['FFmpeg Installation Failed'][current_lang]}: {str(e)}")
        return False


translations = {
    'YouTube Video Downloader': {'en': 'YouTube Video Downloader', 'es': 'Descargador de Videos de YouTube'},
    'Enter YouTube video URL:': {'en': 'Enter YouTube video URL:', 'es': 'Ingrese la URL del video de YouTube:'},
    'Choose video quality:': {'en': 'Choose video quality:', 'es': 'Elija la calidad del video:'},
    'Download': {'en': 'Download', 'es': 'Descargar'},
    'Choose Folder': {'en': 'Choose Folder', 'es': 'Elegir Carpeta'},
    'Folder chosen:': {'en': 'Folder chosen:', 'es': 'Carpeta elegida:'},
    'Download Complete': {'en': 'Download Complete', 'es': 'Descarga Completa'},
    'Audio downloaded and converted to MP3 successfully!': {'en': 'Audio downloaded and converted to MP3 successfully!',
                                                            'es': '¡Audio descargado y convertido a MP3 correctamente!'},
    'Video downloaded and merged successfully!': {'en': 'Video downloaded and merged successfully!',
                                                  'es': '¡Video descargado y fusionado correctamente!'},
    'Video downloaded successfully!': {'en': 'Video downloaded successfully!',
                                       'es': '¡Video descargado correctamente!'},
    'Error': {'en': 'Error', 'es': 'Error'},
    'FFmpeg Not Found': {'en': 'FFmpeg Not Found', 'es': 'FFmpeg No Encontrado'},
    'FFmpeg is required to convert video to MP3. Please install FFmpeg.': {
        'en': 'FFmpeg is required to convert video to MP3. Please install FFmpeg.',
        'es': 'FFmpeg es necesario para convertir video a MP3. Por favor, instale FFmpeg.'},
    'No audio stream found for this video.': {'en': 'No audio stream found for this video.',
                                              'es': 'No se encontró un stream de solo audio para este video.'},
    'No stream found for the selected quality.': {'en': 'No stream found for the selected quality.',
                                                  'es': 'No se encontró un stream para la calidad seleccionada.'},
    'FFmpeg Installation': {'en': 'FFmpeg Installation', 'es': 'Instalación de FFmpeg'},
    'Installing FFmpeg': {'en': 'Installing FFmpeg using winget.', 'es': 'Intentando instalar FFmpeg usando winget.'},
    'FFmpeg Installed': {'en': 'FFmpeg installed successfully. Please restart the application.',
                         'es': 'FFmpeg instalado correctamente. Por favor, reinicie la aplicación.'},
    'Installation Failed': {'en': 'Installation Failed', 'es': 'Instalación Fallida'},
    'FFmpeg Installation Failed': {'en': 'FFmpeg installation failed', 'es': 'Falló la instalación de FFmpeg'},
    'Language': {'en': 'Language', 'es': 'Idioma'},
}

current_lang = 'en'


class YouTubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title(translations['YouTube Video Downloader'][current_lang])

        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        lang_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=translations['Language'][current_lang], menu=lang_menu)
        lang_menu.add_command(label="English", command=lambda: self.change_language('en'))
        lang_menu.add_command(label="Español", command=lambda: self.change_language('es'))

        self.url_label = tk.Label(self.root, text=translations['Enter YouTube video URL:'][current_lang])
        self.url_label.pack()
        self.url_entry = tk.Entry(self.root, width=50)
        self.url_entry.pack()

        self.quality_label = tk.Label(self.root, text=translations['Choose video quality:'][current_lang])
        self.quality_label.pack()
        self.quality_var = tk.StringVar(self.root)
        self.quality_var.set("360p")
        self.quality_menu = tk.OptionMenu(self.root, self.quality_var, "360p", "480p", "720p", "1080p", "1440p",
                                          "2160p", "MP3")
        self.quality_menu.pack()

        self.download_button = tk.Button(self.root, text=translations['Download'][current_lang],
                                         command=self.download_video)
        self.download_button.pack()

        self.status_label = tk.Label(self.root, text="")
        self.status_label.pack()

        self.folder_button = tk.Button(self.root, text=translations['Choose Folder'][current_lang],
                                       command=self.choose_folder)
        self.folder_button.pack()
        self.folder_path = ""

        self.ffmpeg_installed = check_ffmpeg_installed()
        if not self.ffmpeg_installed:
            self.ffmpeg_installed = install_ffmpeg()

    def change_language(self, lang):
        global current_lang
        current_lang = lang
        self.root.title(translations['YouTube Video Downloader'][current_lang])
        self.url_label.config(text=translations['Enter YouTube video URL:'][current_lang])
        self.quality_label.config(text=translations['Choose video quality:'][current_lang])
        self.download_button.config(text=translations['Download'][current_lang])
        self.folder_button.config(text=translations['Choose Folder'][current_lang])

    def choose_folder(self):
        self.folder_path = filedialog.askdirectory()
        self.status_label.config(text=f"{translations['Folder chosen:'][current_lang]}: {self.folder_path}")

    def download_video(self):
        url = self.url_entry.get()
        quality = self.quality_var.get()

        if not self.ffmpeg_installed and quality == "MP3":
            messagebox.showerror(translations['FFmpeg Not Found'][current_lang],
                                 translations['FFmpeg is required to convert video to MP3. Please install FFmpeg.'][
                                     current_lang])
            return

        try:
            yt = pytube.YouTube(url)
            if quality == "MP3":
                stream = yt.streams.filter(only_audio=True).first()
                if stream is None:
                    messagebox.showerror(translations['Error'][current_lang],
                                         translations['No audio stream found for this video.'][current_lang])
                    return
                output_file = stream.download(output_path=self.folder_path)
                base, ext = os.path.splitext(output_file)
                new_file = base + ".mp3"
                AudioSegment.from_file(output_file).export(new_file, format="mp3")
                os.remove(output_file)
                messagebox.showinfo(translations['Download Complete'][current_lang],
                                    translations['Audio downloaded and converted to MP3 successfully!'][current_lang])
            else:
                if quality in ["1080p", "1440p", "2160p"]:
                    video_stream = yt.streams.filter(res=quality, file_extension="mp4").first()
                    audio_stream = yt.streams.filter(only_audio=True, file_extension="mp4").first()
                    if video_stream is None or audio_stream is None:
                        messagebox.showerror(translations['Error'][current_lang],
                                             translations['No stream found for the selected quality.'][current_lang])
                        return
                    video_file = video_stream.download(output_path=self.folder_path, filename="video.mp4")
                    audio_file = audio_stream.download(output_path=self.folder_path, filename="audio.mp4")
                    output_file = os.path.join(self.folder_path, yt.title + ".mp4")
                    command = f'ffmpeg -i "{video_file}" -i "{audio_file}" -c:v copy -c:a aac "{output_file}"'
                    subprocess.run(command, shell=True)
                    os.remove(video_file)
                    os.remove(audio_file)
                    messagebox.showinfo(translations['Download Complete'][current_lang],
                                        translations['Video downloaded and merged successfully!'][current_lang])
                else:
                    stream = yt.streams.filter(res=quality, file_extension="mp4").first()
                    if stream is None:
                        messagebox.showerror(translations['Error'][current_lang],
                                             translations['No stream found for the selected quality.'][current_lang])
                        return
                    stream.download(output_path=self.folder_path)
                    messagebox.showinfo(translations['Download Complete'][current_lang],
                                        translations['Video downloaded successfully!'][current_lang])
        except Exception as e:
            messagebox.showerror(translations['Error'][current_lang], str(e))


def main():
    install_packages()
    global pytube, AudioSegment
    import pytube
    from pydub import AudioSegment

    root = tk.Tk()
    app = YouTubeDownloader(root)
    root.mainloop()


if __name__ == "__main__":
    main()

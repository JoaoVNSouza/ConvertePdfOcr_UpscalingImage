import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageTk
import threading
import os
from ocr_pdf import ocr_pdf
from gemini_imagem import gerar_imagem
from dotenv import load_dotenv

load_dotenv()
PATH_IMAGE_GENERATED = os.environ.get("PATH_IMAGE_GENERATED")

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


def tamanho_tela() -> (int, int):
    root = ctk.CTk()
    largura_tela = root.winfo_screenwidth()
    altura_tela = root.winfo_screenheight()
    root.destroy()

    return largura_tela, altura_tela


def calcula_center_janela(largura_janela, altura_janela):
    largura_tela, altura_tela = tamanho_tela()

    x = (largura_tela // 2) - (largura_janela // 2)
    y = (altura_tela // 2) - (altura_janela // 2) - 50
    return x, y


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        largura_janela = 800
        altura_janela = 600
        x, y = calcula_center_janela(largura_janela, altura_janela)
        fonte = ("Arial", 12)

        self.title("Sistema Catálogo de Roupas - Lança Perfume")
        self.geometry(
            f"{largura_janela}x{altura_janela}+{x}+{y}")

        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)

        # Tabs
        self.tab_ocr = self.tabview.add("PDF Pesquisável")
        self.tab_upscale = self.tabview.add("Melhor Qualidade Imagem")

        self.create_ocr_tab()
        self.create_upscale_tab()

    # ================= OCR TAB =================
    def create_ocr_tab(self):
        self.pdf_path = None
        self.output_path = None

        self.select_pdf_btn = ctk.CTkButton(
            self.tab_ocr,
            text="1º Selecionar PDF",
            command=self.select_pdf
        )
        self.select_pdf_btn.pack(pady=20)

        self.status_label = ctk.CTkLabel(self.tab_ocr, text="")
        self.status_label.pack(pady=10)

        self.select_output_path = ctk.CTkButton(
            self.tab_ocr,
            text="2º Selecionar Pasta Destino",
            command=self.select_output_path
        )
        self.select_output_path.pack(pady=20)

        self.output_label = ctk.CTkLabel(self.tab_ocr, text="")
        self.output_label.pack(pady=10)

        self.progress = ctk.CTkProgressBar(self.tab_ocr)
        self.progress.pack(fill="x", padx=40, pady=20)
        self.progress.set(0)

        self.start_btn = ctk.CTkButton(
            self.tab_ocr,
            text="3º Converter para Pesquisável",
            command=self.start_ocr
        )
        self.start_btn.pack(pady=20)

        self.result_label = ctk.CTkLabel(self.tab_ocr, text="")
        self.result_label.pack(pady=10)

    def select_pdf(self):
        self.pdf_path = filedialog.askopenfilename(
            filetypes=[("PDF Files", "*.pdf")]
        )
        self.status_label.configure(text=f"✅ Selecionado: {self.pdf_path}")

    def select_output_path(self):
        self.output_path = filedialog.askdirectory()
        self.output_label.configure(text=f"✅ Selecionado: {self.output_path}")

    def start_ocr(self):
        if not self.pdf_path:
            return

        self.result_label.configure(
            text="Conversão iniciada... Aguarde por favor...")
        threading.Thread(target=self.run_ocr).start()

    def run_ocr(self):
        # Aqui você chama sua função OCR real
        ocr_pdf(self.pdf_path, self.output_path)

        for i in range(100):
            self.progress.set(i / 100)
            self.update_idletasks()

        self.result_label.configure(
            text="✅ Conversão concluida com sucesso!")

    # ================= UPSCALE TAB =================
    def create_upscale_tab(self):
        self.image_path = None
        self.generated_image_path = None

        self.select_img_btn = ctk.CTkButton(
            self.tab_upscale,
            text="1º Selecionar Imagem",
            command=self.select_image
        )
        self.select_img_btn.pack(pady=20)

        self.image_label = ctk.CTkLabel(self.tab_upscale, text="")
        self.image_label.pack(pady=10)

        self.upscale_btn = ctk.CTkButton(
            self.tab_upscale,
            text="2º Melhor Qualidade Imagem",
            command=self.run_upscale
        )
        self.upscale_btn.pack(pady=20)

        self.result_label_txt = ctk.CTkLabel(self.tab_upscale, text="")
        self.result_label_txt.pack(pady=10)

    def select_image(self):
        self.image_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg")]
        )

        img = Image.open(self.image_path)
        img = img.resize((300, 300))
        self.tk_image = ImageTk.PhotoImage(img)

        self.image_label.configure(image=self.tk_image, text="")

    def run_upscale(self):
        # Aqui você chama sua função IA real
        if not self.image_path:
            return

        self.result_label_txt.configure(
            text="Gerando imagem... Aguarde por favor...")

        rst = gerar_imagem(self.image_path)

        if rst:
            self.result_label_txt.configure(
                text="✅ Imagem gerada com sucesso!")
            # abrir arquivo gerado
            os.startfile(PATH_IMAGE_GENERATED)

        else:
            self.result_label_txt.configure(text="Erro ao gerar imagem!")


if __name__ == "__main__":
    app = App()
    app.mainloop()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# app_copias.py
#
# Copyright (C) 2025 Walter Elias <walter.elias@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import subprocess
import os

class ImageCopierApp:
    def __init__(self):
        # Carga el archivo .glade
        self.builder = Gtk.Builder()
        self.builder.add_from_file("generador_copias.glade")

        # Conecta los handlers definidos en Glade
        self.builder.connect_signals(self)

        # Obtiene referencias a los widgets
        self.window = self.builder.get_object("main_window") # Asegúrate que el ID de tu ventana en Glade sea 'main_window'
        self.file_chooser_button = self.builder.get_object("file_chooser_button")
        self.label_ruta_imagen = self.builder.get_object("label_ruta_imagen")
        self.generate_button = self.builder.get_object("generate_button")
        self.statusbar = self.builder.get_object("statusbar")

        # Variable para almacenar la ruta de la imagen seleccionada
        self.selected_image_path = None
        self.context_id = self.statusbar.get_context_id("app_status")

        # Muestra la ventana
        self.window.show_all()
        self.push_status("Listo. Selecciona una imagen.")

    def push_status(self, message):
        """Helper para actualizar la barra de estado."""
        self.statusbar.pop(self.context_id) # Limpia el mensaje anterior
        self.statusbar.push(self.context_id, message)

    # --- Handlers de señales (coinciden con los definidos en Glade) ---

    def on_window_destroy(self, widget):
        Gtk.main_quit()

    def on_file_chooser_button_file_set(self, widget):
        self.selected_image_path = self.file_chooser_button.get_filename()
        if self.selected_image_path:
            self.label_ruta_imagen.set_text(os.path.basename(self.selected_image_path))
            self.push_status(f"Imagen seleccionada: {os.path.basename(self.selected_image_path)}")
        else:
            self.label_ruta_imagen.set_text("")
            self.push_status("Ninguna imagen seleccionada.")

    def on_generate_button_clicked(self, widget):
        if not self.selected_image_path:
            self.push_status("Error: Primero debes seleccionar una imagen.")
            return

        self.push_status("Generando 4 copias... por favor espera.")
        # Deshabilita el botón mientras se procesa
        self.generate_button.set_sensitive(False)

        try:
            # Directorio de salida (mismo directorio de la imagen original)
            output_dir = os.path.dirname(self.selected_image_path)
            # Nombre del archivo de salida
            base_name = os.path.splitext(os.path.basename(self.selected_image_path))[0]
            output_filename = os.path.join(output_dir, f"{base_name}_4copias.pdf")

            # Construye el comando ImageMagick 'montage'
            # Usamos -density para asegurar una buena resolución en PDF
            # -tile 2x2 para la cuadrícula
            # -geometry +10+10 para 10px de margen
            # $(printf "...") se traduce a 'image.jpg image.jpg image.jpg image.jpg'
            #shell_command = f'montage -density 300 -tile 2x2 -geometry +10+10 "{self.selected_image_path}" "{self.selected_image_path}" "{self.selected_image_path}" "{self.selected_image_path}" "{output_filename}"'
            
            # Una forma más robusta sin usar shell=True, pasando una lista de argumentos
            # Esto evita problemas con espacios en los nombres de archivo
            command_args = [
                "montage",
                "-density", "300", # DPI para el PDF
                "-tile", "2x2",
                "-geometry", "+10+10",
            ]
            # Añade la imagen de entrada 4 veces
            for _ in range(4):
                command_args.append(self.selected_image_path)
            command_args.append(output_filename)

            # Ejecuta el comando
            # stdout=subprocess.PIPE, stderr=subprocess.PIPE permite capturar la salida
            process = subprocess.run(command_args, capture_output=True, text=True, check=True)

            self.push_status(f"¡Éxito! Archivo guardado en: {output_filename}")

        except subprocess.CalledProcessError as e:
            self.push_status(f"Error al generar: {e.stderr.strip()}")
            print(f"Error de ImageMagick: {e.stderr}")
        except FileNotFoundError:
            self.push_status("Error: Asegúrate de que ImageMagick esté instalado (comando 'montage' no encontrado).")
        except Exception as e:
            self.push_status(f"Ocurrió un error inesperado: {e}")
            print(f"Error inesperado: {e}")
        finally:
            self.generate_button.set_sensitive(True) # Habilita el botón de nuevo

# Punto de entrada de la aplicación
if __name__ == "__main__":
    app = ImageCopierApp()
    Gtk.main()

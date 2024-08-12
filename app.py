import sys
import cv2
import threading
from flask import Flask, Response
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QMessageBox


# Variável global para controlar o fluxo da câmara
capture = None

# Função para iniciar a câmara
def start_camera():
    global capture
    capture = cv2.VideoCapture(0)
    if not capture.isOpened():
        QMessageBox.critical(None, "Erro", "Não foi possível acessar a câmara.")
        return

    def show_camera():
        while capture.isOpened():
            ret, frame = capture.read()
            if not ret:
                break
            cv2.imshow('Camera', frame)
            if cv2.waitKey(1) == 27:  # Pressione 'ESC' para sair
                break
        capture.release()
        cv2.destroyAllWindows()

    # Inicia a thread para mostrar o feed da câmara
    threading.Thread(target=show_camera).start()

# Função para iniciar o servidor de streaming
def start_stream_server():
    app = Flask(__name__)

    def gen_frames():
        global capture
        while True:
            success, frame = capture.read()
            if not success:
                break
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    @app.route('/video_feed')
    def video_feed():
        return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

    # Inicia o servidor Flask em uma nova thread
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000)).start()
    QMessageBox.information(None, "Servidor de Streaming", "Servidor iniciado em http://0.0.0.0:5000/video_feed")

# Função para sair da aplicação
def quit_app():
    if capture and capture.isOpened():
        capture.release()
    sys.exit()

# Função principal para configurar a interface do PyQt5
def main():
    app = QApplication(sys.argv)

    # Criação da janela principal
    window = QWidget()
    window.setWindowTitle("Controle de Streaming")

    # Criação dos botões
    btn_start_camera = QPushButton("Ligar Câmara")
    btn_start_camera.clicked.connect(start_camera)

    btn_start_server = QPushButton("Ligar Servidor de Stream")
    btn_start_server.clicked.connect(start_stream_server)

    btn_quit = QPushButton("Sair")
    btn_quit.clicked.connect(quit_app)

    # Configuração do layout
    layout = QVBoxLayout()
    layout.addWidget(btn_start_camera)
    layout.addWidget(btn_start_server)
    layout.addWidget(btn_quit)

    window.setLayout(layout)
    window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

import qrcode

url = "http://192.168.18.132:8000"
img = qrcode.make(url)
img.save("acesso_mobile_qr.png")
print("QR code gerado: acesso_mobile_qr.png\nAponte a câmera do celular para acessar o sistema!")

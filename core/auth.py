import pyotp
import qrcode
import base64
from io import BytesIO

class Auth:

    def create_secret():

        return pyotp.random_base32()
    
    def verify_2fa_code( code, secret ):

        totp = pyotp.TOTP( secret )

        return totp.verify( code )
    
    def get_2fa_link( secret, username, issuer_name ):

        totp = pyotp.TOTP( secret )

        return totp.provisioning_uri( name=username, issuer_name=issuer_name )
    
    def get_qr_code( uri ):

        qr = qrcode.make( uri )

        return qr
    
    def get_qr_code_img( qr ):

        # Convert the QR code to an in-memory bytes buffer
        buffered = BytesIO()
        
        qr.save(buffered, format="PNG")
        
        # Encode the image to base64
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
        # Create the HTML image tag with the base64 string
        img_tag = f'<img src="data:image/png;base64,{img_str}" alt="QR Code">'

        return img_tag
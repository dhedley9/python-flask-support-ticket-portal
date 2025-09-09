import core.config as config
import requests

class Mailer():

    def send_email( to_email, subject, content, plain_text = None ):

        api_key    = Mailer.get_api_key()
        api_url    = Mailer.get_api_url()
        from_email = Mailer.get_from_email()

        auth = ( "api", api_key )
        
        data = {
            "from": from_email,
            "to": [ to_email ],
            "subject": subject,
            "html": content
        }

        if plain_text is not None:
            data['text'] = plain_text

        return requests.post( api_url , auth=auth, data=data )

    def get_from_email():
        return "CA Portal <noreply@" + config.mailgun_domain + ">"
    
    def get_api_url():

        if config.mailgun_region == "us":
            return "https://api.mailgun.net/v3/" + config.mailgun_domain + "/messages"
        else:
            return "https://api.eu.mailgun.net/v3/" + config.mailgun_domain + "/messages"
    
    def get_api_key():
        return config.mailgun_api_key
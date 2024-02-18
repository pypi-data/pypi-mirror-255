from requests import get
from urllib.parse import urlencode


class SMSClient:
    """BulkSMSAPI Wrapper (bulksms.md)\n
    SMSClient object contains two methods: `send_sms_simple` & `send_sms_nde`.

    Args:
        username (str): Nume de utilizator unic al clientului.
        password (str): Parola de acces.
        sender (str): Nume ale senderilor  prestabilite în contract. Maximum 11 simboluri.
        dlrurl (str, optional): Adresa URL care va fi apelată pentru trimiterea raportului DLR. Defaults to `''`.
        dlrmask (int, optional): Mască de biţi, pentru determinarea rapoartelor DLR necesare. Defaults to `31`.
        charset (str, optional): Determină  codificarile în care se trimit textele mesajelor. Codificari disponibile: plaintext, windows-1251, utf8. Defaults to `'utf8'`.
        coding (str, optional): Folosiţi întotdeauna: 2. Defaults to `'2'`.
        proxy (dict, optional): Proxy settings in the following format: `{"http": PROXY_URL, "https": PROXY_URL}`. Defaults to `None`.
    """

    def __init__(
        self,
        username: str,
        password: str,
        sender: str,
        dlrurl: str = "",
        dlrmask: int = 31,
        charset: str = "utf8",
        coding: str = "2",
        proxy: str = None,
    ) -> None:
        self.base_url_simple = (
            "https://api.bulksms.md:4432/UnifunBulkSMSAPI.asmx/SendSMSSimple?"
        )
        self.base_url_nde = "https://api.bulksms.md:4432/UnifunBulkSMSAPI.asmx/SendSMSNoneDigitsEncoded?"
        self.username = username
        self.password = password
        self.sender = sender
        self.dlrurl = dlrurl
        self.dlrmask = dlrmask
        self.charset = charset
        self.coding = coding
        self.proxy = proxy

    def _make_api_request(self, url: str, params: dict) -> dict:
        params["username"] = self.username
        params["password"] = self.password

        return get(url + urlencode(params), proxies=self.proxy)

    def send_sms_simple(self, msisdn: str, body: str, prefix: str = "373") -> dict:
        """SendSMSSimple\n
        Varianta simplă a serviciului,
        care necesită date minime de intrare şi care nu necesită rapoarte de remitere SMS la abonat.
        În acest regim este posibilă trimiterea doar a mesajelor cu texte codificate în format plaintext,
        care conţin doar literele alfabetului latin nu mai mare de 160 de caractere.

        Args:
            msisdn (str): Phone number without prefix.
            body (str): Body of the message.
            prefix (str, optional): Phone number prefix. Defaults to `'373'`.

        Returns:
            dict: Send message request response.
        """

        return self._make_api_request(
            self.base_url_simple,
            {
                "from": self.sender,
                "to": prefix + msisdn,
                "text": body,
            },
        )

    def send_sms_nde(
        self,
        msisdn: str,
        body: str,
        dlrurl: str,
        dlrmask: int,
        charset: str,
        coding: str,
        prefix: str = "373",
    ) -> dict:
        """SendSMSNoneDigitsEncoded\n
        Varianta deplină a serviciului,
        care permite trimiterea mesajelor SMS către abonaţi în diferite standarde de codificare,
        precum şi primirea rapoartelor de remitere a mesajului respectiv către abonat.

        Args:
            msisdn (str): Phone number without prefix.
            body (str): Body of the message.
            prefix (str, optional): Phone number prefix. Defaults to `'373'`.
            dlrurl (str, optional): Adresa URL care va fi apelată pentru trimiterea raportului DLR. Defaults to `SMSClient.dlrurl` property or `''` if not modified.
            dlrmask (int, optional): Mască de biţi, pentru determinarea rapoartelor DLR necesare. Defaults to `SMSClient.dlrmask` property or `31` if not modified.
            charset (str, optional): Determină  codificarile în care se trimit textele mesajelor. Codificari disponibile: plaintext, windows-1251, utf8. Defaults to `SMSClient.charset` property or `'utf8'` if not modified.
            coding (str, optional): Folosiţi întotdeauna: 2. Defaults to `SMSClient.coding` property or `'2'` if not modified.

        Returns:
            dict: Send message request response.
        """

        return self._make_api_request(
            self.base_url_nde,
            {
                "from": self.sender,
                "to": prefix + msisdn,
                "text": body,
                "charset": charset if charset else self.charset,
                "dlrmask": dlrmask if dlrmask else self.dlrmask,
                "dlrurl": dlrurl if dlrurl else self.dlrurl,
                "coding": coding if coding else self.coding,
            },
        )

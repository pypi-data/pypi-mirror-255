import structlog
import requests

logger = structlog.getLogger(__name__)


class EngineDeepL:

    def __init__(self, url: str | None, key: str | None):
        self.url = url
        self.key = key

    def sample(self, text, src_lang, tgt_lang, glossary=None):
        logger.info("[TRANSLATION] [DeepL] SRC_Lang: {} TGT_Lang: {}".format(src_lang, tgt_lang))
        logger.info("[TRANSLATION] [DeepL] Text: {}".format(text))
        headers = {
            'Authorization': self.key,
        }
        data = {
            'text': text,
            'source_lang': src_lang.upper() if "_" not in src_lang else src_lang.split("_")[0].upper(),
            'target_lang': tgt_lang.upper() if "_" not in tgt_lang else tgt_lang.split("_")[0].upper(),
            'glossary_id': glossary if glossary is not None else ""
        }
        if glossary is None:
            del data['glossary_id']
        response = requests.get(self.url, headers=headers, data=data)
        if response.status_code == 200:
            translation = response.json()["translations"][0]["text"]
            logger.info("[TRANSLATION] [DeepL] Translation: {}".format(translation))
            return translation
        else:
            raise Exception(f"[{response.status_code}] [{response.text}] Error DeepL")


__all__ = ["EngineDeepL"]

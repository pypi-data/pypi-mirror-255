from enum import Enum
import re, copy, pickle
from langdetect import detect_langs
import pkg_resources

# ##### #
# Regex # @ https://github.com/nathanshartmann/portuguese_word_embeddings
# ##### #
punctuations = re.escape('!"#%\'()*+,./:;<=>?@[\\]^_`{|}~')
re_remove_brackets = re.compile(r'\{.*\}')
re_remove_html = re.compile(r'<(\/|\\)?.+?>', re.UNICODE)
re_transform_numbers = re.compile(r'\d', re.UNICODE)
re_transform_emails = re.compile(r'[^\s]+@[^\s]+', re.UNICODE)
re_transform_url = re.compile(r'(http|https)://[^\s]+', re.UNICODE)
# Different quotes are used.
re_quotes_1 = re.compile(r"(?u)(^|\W)[‘’′`']", re.UNICODE)
re_quotes_2 = re.compile(r"(?u)[‘’`′'](\W|$)", re.UNICODE)
re_quotes_3 = re.compile(r'(?u)[‘’`′“”]', re.UNICODE)
re_dots = re.compile(r'(?<!\.)\.\.(?!\.)', re.UNICODE)
re_punctuation = re.compile(r'([,";:]){2},', re.UNICODE)
re_hiphen = re.compile(r' -(?=[^\W\d_])', re.UNICODE)
re_tree_dots = re.compile(u'…', re.UNICODE)
# Differents punctuation patterns are used.
re_punkts = re.compile(r'(\w+)([%s])([ %s])' %
                       (punctuations, punctuations), re.UNICODE)
re_punkts_b = re.compile(r'([ %s])([%s])(\w+)' %
                         (punctuations, punctuations), re.UNICODE)
re_punkts_c = re.compile(r'(\w+)([%s])$' % (punctuations), re.UNICODE)
re_changehyphen = re.compile(u'–')
re_doublequotes_1 = re.compile(r'(\"\")')
re_doublequotes_2 = re.compile(r'(\'\')')
re_trim = re.compile(r' +', re.UNICODE)

tokenizer_ptbr = pickle.load(open(pkg_resources.resource_filename('text_util_en_pt', 'resources/portuguese_nltk_tokenizer.pkl'), 'rb'))
tokenizer_enus = pickle.load(open(pkg_resources.resource_filename('text_util_en_pt', 'resources/english_nltk_tokenizer.pkl'), 'rb'))
stopwords_ptbr = list(set(['clt1148028', 'bmetrack', 'nan','coluna', 'tentar', 'iniciar', 'ono', 'pronto', 'id', 'rá', 'ré', 'it', 'az', 'primeiro', 'segundo', 'terceiro', 'quarto', 'quinto', 'sexto', 'sétimo', 'oitavo', 'nono', 'décimo', 'senhor', 'senhora', 'falsar', 'clique', 'sebraepr', 'jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez', 'jananeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro', 'ltda', 'sebrae', 'neste', 'novos', 'per', 'bastante', 'bem', 'devendo', 'houvermos', 'talvez', 'houvéssemos', 'certamente', 'entre', 'lhes', 'estiveste', 'amplas', 'grandes', 'estejamos', 'umas', 'ali', 'sem', 'tivéssemos', 'podiam', 'faz', 'desse', 'tivera', 'nenhum', 'todos', 'obrigada', 'outro', 'tiveram', 'dizer', 'questão', 'boas', 'não', 'perto', 'serão', 'feitas', 'pelas', 'mal', 'ainda', 'és', 'só', 'deveria', 'cá', 'ampla', 'nove', 'disso', 'tivéramos', 'enquanto', 'houveram', 'aquele', 'minha', 'apoio', 'mim', 'forem', 'às', 'meio', 'tinha', 'estes', 'catorze', 'primeira', 'fazemos', 'vais', 'segunda', 'teria', 'devia', 'vão', 'geral', 'dele', 'seria', 'estivessem', 'dez', 'poucos', 'hajam', 'tão', 'nunca', 'deverá', 'noite', 'na', 'estadoadeus', 'momento', 'um', 'sexta', 'máximo', 'relação', 'nesta', 'logo', 'é', 'houveríamos', 'dia', 'estivesse', 'tal', 'quarta', 'lá', 'meses', 'quatro', 'dos', 'mas', 'oito', 'fora', 'sei', 'tivessem', 'porém', 'muitas', 'hajamos', 'quinta', 'poderiam', 'estavam', 'nome', 'trabalho', 'naquele', 'porque', 'tu', 'estivéramos', 'houveria', 'todavia', 'tivermos', 'pequenos', 'fomos', 'sobre', 'poucas', 'nossas', 'hoje', 'mesmas', 'perante', 'houvera', 'são', 'mês', 'daquela', 'hora', 'aquelas', 'próximo', 'nossos', 'num', 'naquelas', 'vários', 'pude', 'uns', 'área', 'mesmos', 'ter', 'sendo', 'obrigado', 'nos', 'estive', 'foram', 'desses', 'esse', 'deste', 'treze', 'terão', 'próximas', 'antes', 'seríamos', 'contra', 'nestes', 'ponto', 'ele', 'lado', 'em', 'tivemos', 'naquela', 'cinco', 'terceira', 'cento', 'dar', 'hão', 'dessa', 'zero', 'dizem', 'vosso', 'dito', 'estão', 'nesses', 'dever', 'final', 'mais', 'até', 'mil', 'quê', 'vossos', 'coisas', 'desta', 'conselho', 'fui', 'fazeis', 'posição', 'tens', 'brasil', 'próximos', 'maior', 'com', 'nova', 'certeza', 'ou', 'tampouco', 'quando', 'vem', 'sétimo', 'cima', 'seremos', 'nenhuma', 'fostes', 'nessas', 'algum', 'sistema', 'https', 'feitos', 'nós', 'deviam', 'si', 'vens', 'nem', 'essas', 'querem', 'tua', 'viagem', 'seis', 'foste', 'assim', 'à', 'nessa', 'te', 'podendo', 'depois', 'pequeno', 'tido', 'naqueles', 'pelo', 'local', 'tenham', 'www', 'quer', 'queres', 'nível', 'tenha', 'aí', 'tiverem', 'feita', 'primeiras', 'todas', 'última', 'meus', 'poder', 'aquela', 'falta', 'fôramos', 'teus', 'dezesseis', 'estás', 'tantas', 'alguém', 'disto', 'novas', 'novo', 'quem', 'teriam', 'estar', 'eram', 'teve', 'este', 'possivelmente', 'próprias', 'algumas', 'tenho', 'vossa', 'estou', 'houverão', 'suas', 'fazem', 'lo', 'esses', 'para', 'menos', 'há', 'tendes', 'dúvida', 'nada', 'deles', 'tive', 'vós', 'muito', 'temos', 'último', 'sua', 'seu', 'embora', 'grande', 'três', 'isto', 'pelos', 'foi', 'paucas', 'se', 'tivesse', 'houvéramos', 'eles', 'esteja', 'breve', 'pouca', 'quanto', 'serei', 'ah', 'fez', 'primeiro', 'demais', 'deveriam', 'deverão', 'custa', 'destas', 'quereis', 'sejamos', 'aquilo', 'ao', 'quais', 'houve', 'nosso', 'deve', 'sete', 'tendo', 'últimas', 'posso', 'quinto', 'pequenas', 'os', 'menor', 'sexto', 'têm', 'teríamos', 'uma', 'põem', 'estivermos', 'estivera', 'http', 'ontem', 'sabem', 'oitavo', 'esta', 'aos', 'podia', 'ela', 'tiver', 'daquele', 'daqueles', 'da', 'duas', 'nestas', 'teremos', 'ver', 'podem', 'a', 'oitava', 'onze', 'nas', 'mesma', 'parte', 'la', 'outros', 'pouco', 'houverem', 'haja', 'vos', 'pequena', 'desde', 'tarde', 'diante', 'outras', 'dela', 'boa', 'maioria', 'partir', 'elas', 'vêm', 'põe', 'dentro', 'fossem', 'toda', 'forma', 'algo', 'fazendo', 'quero', 'própria', 'outra', 'éramos', 'seriam', 'favor', 'tiveste', 'tivestes', 'houvessem', 'fazes', 'ai', 'houvesse', 'ti', 'isso', 'tenhamos', 'nesse', 'tanto', 'estamos', 'longe', 'fôssemos', 'está', 'pontos', 'muitos', 'devem', 'número', 'próprio', 'parece', 'o', 'segundo', 'ano', 'dezessete', 'seja', 'vendo', 'atrás', 'meu', 'alguns', 'teu', 'no', 'feito', 'do', 'agora', 'dezoito', 'me', 'era', 'as', 'sois', 'tanta', 'debaixo', 'pela', 'também', 'estávamos', 'sejam', 'sido', 'através', 'grupo', 'quantos', 'estiver', 'já', 'estiveram', 'quarto', 'disse', 'somos', 'sou', 'queremos', 'dão', 'estivestes', 'estas', 'tuas', 'esteve', 'terei', 'cada', 'todo', 'doze', 'houver', 'tinham', 'alguma', 'dessas', 'ó', 'estivemos', 'tudo', 'tem', 'for', 'vir', 'houveriam', 'lugar', 'aqui', 'houverei', 'coisa', 'das', 'estava', 'sempre', 'estiverem', 'vez', 'essa', 'houverá', 'fim', 'puderam', 'vai', 'nossa', 'será', 'como', 'porquê', 'vezes', 'vinte', 'ninguém', 'poderia', 'exemplo', 'cedo', 'eu', 'qual', 'diz', 'sétima', 'estejam', 'após', 'fazer', 'próxima', 'sob', 'pois', 'houveremos', 'minhas', 'amplo', 'possível', 'delas', 'terá', 'havemos', 'tínhamos', 'daquelas', 'bons', 'sim', 'fosse', 'hei', 'destes', 'numa', 'dá', 'houvemos', 'aqueles', 'por', 'primeiros', 'além', 'lhe', 'dezenove', 'horas', 'próprios', 'baixo', 'seus', 'vocês', 'últimos', 'ser', 'faço', 'que', 'havia', 'quinze', 'e', 'amplos', 'de', 'onde', 'obra', 'pode', 'bom', 'apenas', 'muita', 'mesmo', 'contudo', 'anos', 'vossas', 'sabe', 'vindo', 'você', 'pôde', 'dois', 'tém', 'formos', 'ante', 'estivéssemos', 'ano', 'área', 'baixo', 'dar', 'dia', 'grupo', 'local', 'maior', 'máximo', 'noite', 'número', 'obra', 'questão', 'relação', 'viagem', 'capitar', 'industriar' , 'includeeditpanificar', 'caminho', 'estado', 'tempo', 'tipo', 'valor', 'verdade', 'x', 'h', 'www', 'inc', 'http', 'https', 'apontar', 'inciar', 'ligado', 'saber', 'trabalhar', 'usar']))
stopwords_enus = list(set(["trademark","nan", "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves", "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", "with", "about", "against", "between", "into", "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now", "aren't", "can't", "cannot", "could", "couldn't", "didn't", "doesn't", "don't", "hadn't", "hasn't", "haven't", "he'd", "he'll", "he's", "here's", "how's", "i'd", "i'll", "i'm", "i've", "isn't", "it's", "let's", "mustn't", "ought", "shan't", "she'd", "she'll", "she's", "shouldn't", "that's", "there's", "they'd", "they'll", "they're", "they've", "wasn't", "we'd", "we'll", "we're", "we've", "weren't", "what's", "when's", "where's", "who's", "why's", "won't", "would", "wouldn't", "you'd", "you'll", "you're", "you've"]))

class Language(Enum):
    ptbr = 'ptbr'
    enus = 'enus'

def detect_language(text):
    try:
        langs = detect_langs(text)
        if len(langs) > 0:
            det_lng = str(langs[0]).split(':')[0]

            return Language.ptbr if det_lng == 'pt' else Language.enus
    except Exception as e:
        print(e)

    return Language.enus

def remove_repeated_text_improved(text):
    """
    Remove repeated sections from a string, with improved handling of partial overlaps.
    
    The function first splits the text into sentences. It then iteratively checks
    if any sentence is repeating by looking ahead in the list of sentences.
    If a repetition is found, it handles partial overlaps at the boundaries of detected repetitions.
    """
    # Splitting the text into sentences
    sentences = text.split('. ')
    unique_sentences = []

    i = 0
    while i < len(sentences):
        sentence = sentences[i]
        if sentence not in unique_sentences:
            unique_sentences.append(sentence)
            i += 1
        else:
            # Check for partial overlaps at the boundaries
            j = i
            while j < len(sentences) and sentences[j] == sentence:
                j += 1
            # Check if the next few sentences after j form a repeating pattern
            if j < len(sentences):
                next_sentence = sentences[j]
                if next_sentence in unique_sentences:
                    # Skip the overlapping section
                    overlap_index = unique_sentences.index(next_sentence)
                    i = j + (len(unique_sentences) - overlap_index)
                else:
                    unique_sentences.append(sentence)
                    i += 1
            else:
                i = j  # Skip the repeated section

    # Joining the unique sentences back into a string
    return '. '.join(unique_sentences)

def preprocessing(texto):
    replace_dict = {"\t": " ", "<": " ", ">": " ", "‹": " ", "›": " ", "~": " ", "¿": "", 
                    "[": "", "]": "", "%": "", "|": "", "º": "", "+": "", "/": " ", 
                    "\\n": " ", "\\": " ", "“": "\"", "”": "\"", "‘": " ", "’": " ", "�": " "}
    for old_char, new_char in replace_dict.items():
        texto = texto.replace(old_char, new_char)
    texto = texto.lower()
    while '  ' in texto:
        texto = texto.replace('  ', ' ')
    while '..' in texto:
        texto = texto.replace('..', '.')
    return texto

def light_preprocessing(text):
    text = preprocessing(text)
    text = text.lower()
    text = text.replace('\xa0', ' ')
    text = re_tree_dots.sub('...', text)
    text = re.sub('\.\.\.', '', text)
    text = re_remove_brackets.sub('', text)
    text = re_changehyphen.sub('-', text)
    text = re_remove_html.sub(' ', text)
    text = re_quotes_1.sub(r'\1"', text)
    text = re_quotes_2.sub(r'"\1', text)
    text = re_quotes_3.sub('"', text)
    text = re_hiphen.sub(' - ', text)
    text = re_punkts.sub(r'\1 \2 \3', text)
    text = re_punkts_b.sub(r'\1 \2 \3', text)
    text = re_punkts_c.sub(r'\1 \2', text)
    text = re_trim.sub(' ', text)
    text = re_doublequotes_1.sub('\"', text)
    text = re_doublequotes_2.sub('\'', text)
    while '--' in text:
        text = text.replace('--', '-')
    while '==' in text:
        text = text.replace('==', '=')
    while '  ' in text:
        text = text.replace('  ', ' ')
    while '..' in text:
        text = text.replace('..', '.')
    text = text.replace(' ,', ',').replace(' .', '.')
    return text.strip()

def remove_null_chars(input_string):
    return input_string.replace('\u0000', '')

def replace_escaped_unicode(input_string):
    def decode_match(match):
        return bytes(match.group(), 'latin1').decode('unicode_escape')

    return re.sub(r'\\u00[0-9a-fA-F]{2}', decode_match, input_string)

def apply_tokenization(text, lang):
    return tokenizer_ptbr.tokenize(text) if lang == Language.ptbr else tokenizer_enus.tokenize(text)

def split_string_into_sentences(text, sentence_length):
    words = text.split()
    sentences = []
    current_sentence = []

    for word in words:
        current_sentence.append(word)

        if len(current_sentence) >= sentence_length:
            sentences.append(' '.join(current_sentence))
            current_sentence = []

    if current_sentence:
        sentences.append(' '.join(current_sentence))

    return sentences

def remove_empty_sentences(sentences):
    # Remove the empty sentences and store the removed indexes in a variable
    removed_indexes = []
    for index, sentence in enumerate(sentences):
        if len(sentence) <= 2:
            removed_indexes.append(index)

    # Remove the empty sentences from the list
    for index in reversed(removed_indexes):
        sentences.pop(index)

    return sentences, removed_indexes

def is_number(val):
    val = val.strip()
    val = val.replace("-", "")
    return val.replace(".", "", 1).isnumeric()

def simple_text_preprocess(sentences):
    for i in range(len(sentences)):
        text = sentences[i]
        while '  ' in text:
            text = text.replace('  ', ' ')
        
        sentences[i] = text.strip()
        
    return sentences

def preprocessing1(text):
    """Apply all regex above to a given string."""
    text = text.lower()
    text = text.replace('\xa0', ' ')
    text = re_tree_dots.sub('...', text)
    text = re.sub('\.\.\.', '', text)
    text = re_remove_brackets.sub('', text)
    text = re_changehyphen.sub('-', text)
    text = re_remove_html.sub(' ', text)
    text = re_transform_numbers.sub('0', text)
    text = re_transform_url.sub('URL', text)
    text = re_transform_emails.sub('EMAIL', text)
    text = re_quotes_1.sub(r'\1"', text)
    text = re_quotes_2.sub(r'"\1', text)
    text = re_quotes_3.sub('"', text)
    text = re.sub('"', '', text)
    text = re_dots.sub('.', text)
    text = re_punctuation.sub(r'\1', text)
    text = re_hiphen.sub(' - ', text)
    text = re_punkts.sub(r'\1 \2 \3', text)
    text = re_punkts_b.sub(r'\1 \2 \3', text)
    text = re_punkts_c.sub(r'\1 \2', text)
    text = re_doublequotes_1.sub('\"', text)
    text = re_doublequotes_2.sub('\'', text)
    text = re_trim.sub(' ', text)
    return text.strip()

def preprocessing2(texto, clear_stopwords=False):
    texto_limpo = ""
    replace_dict = {",": " ", "\t": " ", "©": " ", ";": " ", ":": " ", "_": " ", "<": " ",
                        ">": " ", "‹": " ", "›": " ", "~": " ", "¿": "", "?": "", "(": "",
                        ")": "", "[": "", "]": "", "%": "", "#": "", "|": "", "º": "", 
                        "+": "", "/": " ", "\\n": " ", "\\": " ", "\"": " ", "“": " ", 
                        "”": " ", "‘": " ", "’": " ", "�": " "}
    for old_char, new_char in replace_dict.items():
        texto = texto.replace(old_char, new_char)
    texto = texto.lower()

    while '  ' in texto:
        texto = texto.replace('  ', ' ')
    
    while '..' in texto:
        texto = texto.replace('..', '.')

    if not clear_stopwords:
        return texto

    palavras = texto.split(" ")
    for palavra in palavras:
        palavra = palavra.strip()
        if is_number(palavra):
            continue
        if palavra != "" and palavra not in stopwords_ptbr and palavra not in stopwords_enus and len(palavra) > 2 and len(palavra) < 50:
            texto_limpo += palavra + " "
    if texto_limpo != "":
        texto_limpo = texto_limpo[:-1]
        return texto_limpo
    else:
        return None
    
def preprocessing_pipeline(text):
    try:
        text = preprocessing1(text)
        text = preprocessing2(text, clear_stopwords=False)
        text = simple_text_preprocess([text])[0]
        return text
    except Exception:
        return ""
    
def remove_duplicates(sentences):
    seen = {}
    removed_indexes = []

    for index, item in enumerate(sentences):
        if item not in seen:
            seen[item] = True
        else:
            removed_indexes.append(index)

    sentences = [item for index, item in enumerate(sentences) if index not in removed_indexes]
    return sentences, removed_indexes

def get_sentences_from_raw_text(raw_text, sentence_length):
    raw_text = raw_text.replace('\\', '').replace('-\n', '').replace('\n', ' ')
    raw_text = preprocessing(raw_text)

    detected_language = detect_language(raw_text)
    sentences = apply_tokenization(raw_text, detected_language)
    sentences = ' '.join(sentences)
    # Create sentences from text. Each sentence is a string and should have 'sentence_length' words
    sentences = split_string_into_sentences(sentences, sentence_length)
    sentences, _ = remove_empty_sentences(sentences)

    # Check sentences that are too long and split if needed
    final_sentences = []
    for s in sentences:
        try:
            if len(s.split()) > sentence_length:
                words = s.split()
                num_parts = len(words) // sentence_length + 1
                for i in range(num_parts):
                    start_index = i * sentence_length
                    end_index = (i + 1) * sentence_length
                    part = " ".join(words[start_index:end_index])
                    final_sentences.append(part)
            else:
                final_sentences.append(s)
        except Exception as e:
            print(e)

    original_sentences = copy.deepcopy(final_sentences)
    final_sentences = [ preprocessing_pipeline(sentence) for sentence in final_sentences ]
    sentences, removed_indexes = remove_empty_sentences(final_sentences)

    # Remove the indexes from the original_sentences
    for index in reversed(removed_indexes):
        original_sentences.pop(index)

    # Remove duplicates but keep the order
    sentences, removed_indexes = remove_duplicates(sentences)

    # Remove the indexes from the original_sentences
    for index in reversed(removed_indexes):
        original_sentences.pop(index)
    
    preprocessed_sentences = simple_text_preprocess(sentences)

    del sentences, removed_indexes, final_sentences

    return preprocessed_sentences, original_sentences

def unify_sentences_target_sentence_length(preprocessed_sentences, original_sentences, target_sentence_length):
    def merge_sentences(sentences, word_count):
        merged_sentences = []
        current_sentence = []
        current_count = 0
        indices = []

        for i, sentence in enumerate(sentences):
            words = sentence.split()
            if current_count + len(words) <= word_count:
                current_sentence.extend(words)
                current_count += len(words)
                indices.append(i)
            else:
                merged_sentences.append((' '.join(current_sentence), indices))
                current_sentence = words
                current_count = len(words)
                indices = [i]

        # Adding the last sentence if it's not empty
        if current_sentence:
            merged_sentences.append((' '.join(current_sentence), indices))

        return merged_sentences

    merged_preprocessed_sentences = merge_sentences(preprocessed_sentences, target_sentence_length)

    # Apply same process to original sentences
    merged_sentences = []
    for _, indices in merged_preprocessed_sentences:
        merged_sentence = ' '.join(original_sentences[i] for i in indices)
        merged_sentences.append(merged_sentence)

    return [ s for s, _ in merged_preprocessed_sentences ], merged_sentences

def process_text(text_content, sentence_length):
    try:
        text_content = light_preprocessing(remove_repeated_text_improved(text_content))
        text_content = remove_null_chars(replace_escaped_unicode(text_content))

        preprocessed_sentences, original_sentences = get_sentences_from_raw_text(text_content, sentence_length)

        if len(preprocessed_sentences) != len(original_sentences):
            return None, None

        preprocessed_sentences, original_sentences = unify_sentences_target_sentence_length(preprocessed_sentences, original_sentences, sentence_length)
        preprocessed_sentences_final = preprocessed_sentences

        # Correção de sentenças vazias
        preprocessed_sentences_final, removed_indexes = remove_empty_sentences(preprocessed_sentences_final)

        # Remove the indexes from the original_sentences
        for index in reversed(removed_indexes):
            original_sentences.pop(index)

        # Remove duplicates but keep the order
        preprocessed_sentences_final, removed_indexes = remove_duplicates(preprocessed_sentences_final)

        # Remove the indexes from the original_sentences
        for index in reversed(removed_indexes):
            original_sentences.pop(index)

        return [ {
                'sentence_index': sentence_index,
                'sentence': original_sentences[sentence_index],
        } for sentence_index in range(len(preprocessed_sentences_final))]
    
    except Exception as e:
        print(e)
    
    return []

def structurize_text(text, sentence_length = 150):
    try:
        return process_text(text, sentence_length)
    except Exception as e:
        print(e)

    return None

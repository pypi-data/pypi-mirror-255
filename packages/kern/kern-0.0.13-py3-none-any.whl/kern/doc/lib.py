__all__ = [
    'is_doc',
    'doc_to_text',
]

DOC_TYPES = {'docx', 'odt', 'rtf'}

def is_doc(bytes):
    from kern import infer_type
    return infer_type(bytes) in DOC_TYPES

def doc_to_text(arg):
    import shutil
    import pypandoc
    import assure
    from kern import infer_type
    if not shutil.which('pandoc'):
        pypandoc.download_pandoc(delete_installer=True)
    bytes = assure.bytes(arg)
    type = infer_type(bytes)
    text = pypandoc.convert_text(bytes, 'plain', format=type)
    return text

to_text = doc_to_text

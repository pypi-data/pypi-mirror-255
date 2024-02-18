from pathlib import Path
from typing import Union, Optional
from . import emailer

def uniquify(path:Union[str,Path], counter:int=0) -> Path:
    """
    If the path already exists, append a counter to it. Increment that counter until the path is unique.
    If the path does not already exist, return it as is.
    """
    if isinstance(path, str):
        path = Path(path)
    path = path.resolve()
    if counter != 0:
        candidate_path = path.parent / f"{path.stem}({counter}){path.suffix}"
    else:
        candidate_path = path
    if not candidate_path.exists():
        return candidate_path
    counter += 1
    return uniquify(path, counter)

def make_draft_email(
    out_path:Union[str,Path],
    subject_text:str="",
    body:str="",
    attachments:Optional[list]=None,
    recipients:Optional[list]=None,
    overwrite:bool=False,
):
    if attachments is None:
        attachments = []
    if recipients is None:
        recipients = []
    emailer.create_email_file(
        recipients=recipients,
        subject_text=subject_text,
        out_path=out_path,
        attachments=attachments,
        body=body,
        overwrite=overwrite,
        )


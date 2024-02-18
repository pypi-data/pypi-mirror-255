import octk

attachment=r"test\data\inputs\test_attachment.txt"
outpath = r"test\data\outputs\test_email.eml"

octk.make_draft_email(
    out_path=outpath,
    subject_text="Test Subject",
    body="Test Body raaaaaah!\nhi sll\nhope you're having ufn",
    attachments=[attachment],
    recipients=["alexander.oakley@cfs.com.au"],
)
octk.emailer.create_email_file_2(
    out_path=outpath,
    subject_text="Test Subject",
    body="Test Body raaaaaah!\nhi sll\nhope you're having ufn",
    attachments=[attachment],
    recipients=["alexander.oakley@cfs.com.au"],
)

# %%
# Path: test/test_email.py
# Compare this snippet from src/octk/email.py:
# import octk
#   
# def create_email_file(
#         recipients:list[str],
#         body="",
#         subject_text:str="",
#         out_path:Optional[Union[str,Path]]=None,
#         attachments:Optional[list[Union[str,Path]]]=None,
#         # is_draft=True,
# ):
#     if attachments is None:   
#         attachments=[]
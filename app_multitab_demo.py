import os 
import lightning as L
import gradio as gr

from lightning.app.frontend import StreamlitFrontend
from lightning_app.utilities.state import AppState
from streamlit_option_menu import option_menu
from lightning.app.components.serve import ServeGradio

def _streamlit_home(state: AppState):
    import streamlit as st
    _style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
    st.markdown(_style, unsafe_allow_html=True)
    st.write("Not Implemented")

class LitStreamlitHome(L.LightningFlow):
    def configure_layout(self):
        return StreamlitFrontend(render_fn=_streamlit_home)

class QuestionAnsweringServeGradio(ServeGradio):
    inputs = [
        gr.inputs.Textbox(lines=10, label="Context", placeholder="Type a sentence or paragraph here."), 
        gr.inputs.Textbox(lines=2, label="Question", placeholder="Ask a question based on the context."),
    ]
    outputs = [
        gr.outputs.Textbox(label="Answer"),
        gr.outputs.Label(label="Score"),
    ]
    enable_queue = True
    examples = [
        ["Harry James Potter (DOB: 31 July, 1980) was a half-blood wizard, and one of the most famous wizards of modern times. He was the only child and son of James and Lily Potter, both members of the original Order of the Phoenix. Harry's birth was overshadowed by a prophecy, naming either himself or Neville Longbottom as the one with the power to vanquish Lord Voldemort. After half of the prophecy was reported to Voldemort, courtesy of Severus Snape, Harry was chosen as the target due to his many similarities with the Dark Lord. This caused the Potter family to go into hiding. Voldemort made his first vain attempt to circumvent the prophecy when Harry was a year and three months old. During this attempt he murdered Harry's parents as they tried to protect him, but this unsuccessful attempt to kill Harry led to Voldemort's first downfall. This downfall marked the end of the First Wizarding War, and to Harry henceforth being known as the \"Boy Who Lived\".", 
        "What is the first character's name?"],
        ["Hermione Jean Granger (DOB 19 September, 1979) was an English Muggle-born witch born to Mr and Mrs Granger. At the age of eleven, she learned about her magical nature and was accepted into Hogwarts School of Witchcraft and Wizardry. Hermione began attending Hogwarts in 1991 and was Sorted into Gryffindor House. She possessed a brilliant academic mind and proved to be a gifted student in almost every subject that she studied, to the point where she was nearly made a Ravenclaw by the Sorting Hat.", 
        "What is the first character's gender?"],
    ]

    def __init__(self, cloud_compute, *args, **kwargs):
        super().__init__(*args, cloud_compute=cloud_compute, **kwargs)
        self.ready = False  # required

    def build_model(self):
        pass

    def predict(self, context, question):
        print(question)
        return context

class ImageSegmentationServeGradio(ServeGradio):
    inputs = gr.inputs.Image(type="pil", label="Image")  # required
    outputs = gr.outputs.Image(type="pil")  # required
    examples = [os.path.join(str("./images"), f) for f in os.listdir("./images")]

    def __init__(self, cloud_compute, *args, **kwargs):
        super().__init__(*args, cloud_compute=cloud_compute, **kwargs)
        self.ready = False  # required

    def predict(self, img):
        return img

    def build_model(self):
        pass

class LitRootFlow(L.LightningFlow):
    def __init__(self):
        super().__init__()
        self.home = LitStreamlitHome()
        self.qas = QuestionAnsweringServeGradio(L.CloudCompute("cpu"))
        self.ims = ImageSegmentationServeGradio(L.CloudCompute("cpu"))

    def configure_layout(self):
        tabs = []
        tabs.append({"name": "Home", "content": self.home})
        tabs.append({"name": "Question Answering", "content": self.qas})
        tabs.append({"name": "Image Segmentation", "content": self.ims})
        return tabs

    def run(self):
        self.home.run()
        self.ims.run()
        self.qas.run()
    
app = L.LightningApp(LitRootFlow())
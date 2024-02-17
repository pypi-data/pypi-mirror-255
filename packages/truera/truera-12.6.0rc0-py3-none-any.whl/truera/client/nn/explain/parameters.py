import inspect
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple

from trulens.nn.models._model_base import ModelWrapper

from truera.client.nn.client_configs import LayerAnchor
from truera.client.nn.wrappers.nlp import Wrappers as NLP
from truera.client.util.types import Function
from truera.client.util.types import HelpInfo
from truera.client.util.types import Intersection
from truera.client.util.types import Parameter
from truera.client.util.types import TypeMatching
from truera.client.util.types import Union

PTokenizerWrapper = Parameter(
    "tokenizer_wrapper",
    desc="Tokenizer wrapper. See NLP.TokenizerWrapper for structure.",
    typ=NLP.TokenizerWrapper,
    help_info=HelpInfo(
        definition=[
            "# Using tokenizer_wrapper with Explainer is not recommended",
            "# See nlp_quickstart_pytorch.ipynb and nlp_quickstart_tf2.ipynb for examples",
            "tokenizer_wrapper = None"
        ],
        args_map={"tokenizer_wrapper": "tokenizer_wrapper"}
    )
)
PModelLoadWrapper = Parameter(
    "model_load_wrapper",
    desc="Model load wrapper. See NLP.ModelLoadWrapper for structure.",
    typ=NLP.ModelLoadWrapper,
    help_info=HelpInfo(
        definition=[
            "# Using model_load_wrapper with Explainer is not recommended",
            "# See nlp_quickstart_pytorch.ipynb and nlp_quickstart_tf2.ipynb for examples",
            "model_load_wrapper = None"
        ],
        args_map={"model_load_wrapper": "model_load_wrapper"}
    )
)
PModelRunWrapper = Parameter(
    "model_run_wrapper",
    desc="Model run wrapper. See NLP.ModelRunWrapper for structure.",
    typ=NLP.ModelRunWrapper,
    help_info=HelpInfo(
        definition=[
            "# Using model_run_wrapper with Explainer is not recommended",
            "# See nlp_quickstart_pytorch.ipynb and nlp_quickstart_tf2.ipynb for examples",
            "model_run_wrapper = None"
        ],
        args_map={"model_run_wrapper": "model_run_wrapper"}
    )
)
PSplitLoadWrapper = Parameter(
    "split_load_wrapper",
    desc="Split load wrapper. See NLP.SplitLoadWrapper for structure.",
    typ=NLP.SplitLoadWrapper,
    help_info=HelpInfo(
        definition=[
            "# Using split_load_wrapper with Explainer is not recommended",
            "# See nlp_quickstart_pytorch.ipynb and nlp_quickstart_tf2.ipynb for examples",
            "split_load_wrapper = None"
        ],
        args_map={"split_load_wrapper": "split_load_wrapper"}
    )
)

PVocab = Parameter(
    "vocab",
    desc=
    "A mapping of tokens (str) to token IDs (int). This may be inferrable from some tokenizers.",
    help_info=HelpInfo(
        definition=["vocab = {'<PAD>': 0, 'a': 1, 'b': 2, ...}"],
        args_map={"vocab": "vocab"}
    ),
    typ=Dict[str, int]
)

PUnkTokenId = Parameter(
    "unk_token_id",
    desc=
    "The ID of the token used to represent unknown/out of vocabulary tokenizations.",
    help_info=HelpInfo(
        parameter_deps={"vocab": PVocab},
        definition=[
            # "vocab = {vocab}",
            "unk_token_id = vocab['<UNK>']"
        ],
        args_map={"unk_token_id": "unk_token_id"}
    ),
    typ=int
)

PPadTokenId = Parameter(
    "pad_token_id",
    desc="The ID of the padding token.",
    help_info=HelpInfo(
        parameter_deps={"vocab": PVocab},
        definition=["pad_token_id = vocab['<PAD>']"],
        args_map={"pad_token_id": "pad_token_id"}
    ),
    typ=int
)

PSpecialTokens = Parameter(
    "special_tokens",
    desc=
    "A list of 'special' tokens that should not be considered when computing influences. This may include, PAD, SOS, EOS, UNK, etc.",
    typ=List[int],
    help_info=HelpInfo(
        parameter_deps={"vocab": PVocab},
        definition=["special_tokens = [vocab['<PAD>'], vocab['<UNK>']]"],
        args_map={"special_tokens": "special_tokens"}
    ),
)


# Here only for its signature:
def example_model(*args, **kwargs) -> Any:
    ...


TBlackboxModel = Function(inspect.signature(example_model))
PModelBlackbox = Parameter(
    "model_blackbox",
    typ=TBlackboxModel,
    desc="Blackbox model.",
    help_info=HelpInfo(
        definition=[
            inspect.cleandoc(
                """
            def model_blackbox(*args, **kwargs):
                # replace with your model logic
                outputs = process_inputs(*args, **kwargs)
                return outputs
            """
            )
        ],
        args_map={"model": "model_blackbox"}
    )
)

TTorchModel = 'torch.nn.Module'
TTF1Model = 'tensorflow.Graph'
TTF2Model = Union(
    'keras.engine.training.Model', 'tensorflow.keras.Model',
    'tensorflow_hub.keras_layer.KerasLayer', 'tensorflow.estimator.Estimator'
)

PModelTorch = Parameter(
    "model_torch",
    typ=TTorchModel,
    desc="A pytorch model.",
    help_info=HelpInfo(
        imports="torch",
        definition=[
            inspect.cleandoc(
                """
            class Model(torch.nn.Module):
                def __init__(self):
                    super().__init__()
                    self.linear = torch.nn.Linear(1, 1)

                def forward(self, x):
                    return self.linear(x)
            """
            ), "model_torch = Model()"
        ],
        args_map={"model": "model_torch"}
    )
)
PModelTF1 = Parameter(
    "model_tf1",
    typ=TTF1Model,
    desc="A tensorflow 1 model.",
    help_info=HelpInfo(
        imports="tensorflow as tf",
        definition=[
            inspect.cleandoc(
                """
            # Example Tensorflow 1 model using Keras
            model_tf1 = tf.keras.Sequential([
                keras.layers.Flatten(input_shape=(28, 28)),
                keras.layers.Dense(10, activation=tf.nn.softmax)
            ])
            model_tf1.compile(
                optimizer='adam',
                loss='sparse_categorical_crossentropy',
                metrics=['accuracy']
            )
            """
            )
        ],
        args_map={"model": "model_tf1"}
    )
)
PModelTF2 = Parameter(
    "model_tf2",
    typ=TTF2Model,
    desc="A tensorflow 2 model.",
    help_info=HelpInfo(
        imports="tensorflow as tf",
        definition=[
            inspect.cleandoc(
                """
            # Example Tensorflow 2 model using Keras
            # 
            model_tf2 = tf.keras.Sequential([
                keras.layers.Flatten(input_shape=(28, 28)),
                keras.layers.Dense(10, activation=tf.nn.softmax)
            ])
            model_tf2.compile(
                optimizer='adam',
                loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                metrics=['accuracy']
            )
            """
            )
        ],
        args_map={"model": "model_tf2"}
    )
)

PModel = Parameter(
    "model",
    typ=Union(TTorchModel, TTF1Model, TTF2Model, TBlackboxModel),
    desc="A Model.",
    help_info=PModelTorch.help_info
)

# Huggingface base model classes. These are the ones that would be included as
# part of a feature extractor followed by a classifier architecture.
# Output of:
#print(concretize(
#    transformers.models, pattern=re.compile(r"transformers\..+Model")
#))

PHugsModelName = Parameter(
    "huggingface_model_name",
    desc="The name of a huggingface model.",
    typ=str,
    help_info=HelpInfo(
        definition=[
            "huggingface_model_name = 'bert-base-uncased' # TODO: Replace me"
        ],
        args_map={"model_name": "huggingface_model_name"}
    ),
)

PModelHugsBase = Parameter(
    "huggingface_model_base",
    desc="Base huggingface model.",
    typ=Union(
        'transformers.models.albert.modeling_albert.AlbertModel',
        'transformers.models.albert.modeling_albert.AlbertPreTrainedModel',
        'transformers.modeling_utils.PreTrainedModel',
        'transformers.models.auto.modeling_auto.AutoModel',
        'transformers.models.bart.modeling_bart.BartModel',
        'transformers.models.bart.modeling_bart.BartPretrainedModel',
        'transformers.models.bart.modeling_bart.PretrainedBartModel',
        'transformers.models.beit.modeling_beit.BeitModel',
        'transformers.models.beit.modeling_beit.BeitPreTrainedModel',
        'transformers.models.bert.modeling_bert.BertLMHeadModel',
        'transformers.models.bert.modeling_bert.BertModel',
        'transformers.models.bert.modeling_bert.BertPreTrainedModel',
        'transformers.models.bert_generation.modeling_bert_generation.BertGenerationPreTrainedModel',
        'transformers.models.big_bird.modeling_big_bird.BigBirdModel',
        'transformers.models.big_bird.modeling_big_bird.BigBirdPreTrainedModel',
        'transformers.models.bigbird_pegasus.modeling_bigbird_pegasus.BigBirdPegasusModel',
        'transformers.models.bigbird_pegasus.modeling_bigbird_pegasus.BigBirdPegasusPreTrainedModel',
        'transformers.models.blenderbot.modeling_blenderbot.BlenderbotModel',
        'transformers.models.blenderbot.modeling_blenderbot.BlenderbotPreTrainedModel',
        'transformers.models.blenderbot_small.modeling_blenderbot_small.BlenderbotSmallModel',
        'transformers.models.blenderbot_small.modeling_blenderbot_small.BlenderbotSmallPreTrainedModel',
        'transformers.models.bloom.modeling_bloom.BloomModel',
        'transformers.models.bloom.modeling_bloom.BloomPreTrainedModel',
        'transformers.models.camembert.modeling_camembert.CamembertModel',
        'transformers.models.roberta.modeling_roberta.RobertaModel',
        'transformers.models.canine.modeling_canine.CanineModel',
        'transformers.models.canine.modeling_canine.CaninePreTrainedModel',
        'transformers.models.clip.modeling_clip.CLIPModel',
        'transformers.models.clip.modeling_clip.CLIPPreTrainedModel',
        'transformers.models.clip.modeling_clip.CLIPTextModel',
        'transformers.models.clip.modeling_clip.CLIPVisionModel',
        'transformers.models.codegen.modeling_codegen.CodeGenModel',
        'transformers.models.codegen.modeling_codegen.CodeGenPreTrainedModel',
        'transformers.models.convbert.modeling_convbert.ConvBertModel',
        'transformers.models.convbert.modeling_convbert.ConvBertPreTrainedModel',
        'transformers.models.convnext.modeling_convnext.ConvNextModel',
        'transformers.models.convnext.modeling_convnext.ConvNextPreTrainedModel',
        'transformers.models.ctrl.modeling_ctrl.CTRLLMHeadModel',
        'transformers.models.ctrl.modeling_ctrl.CTRLModel',
        'transformers.models.ctrl.modeling_ctrl.CTRLPreTrainedModel',
        'transformers.models.cvt.modeling_cvt.CvtModel',
        'transformers.models.cvt.modeling_cvt.CvtPreTrainedModel',
        'transformers.models.data2vec.modeling_data2vec_audio.Data2VecAudioModel',
        'transformers.models.data2vec.modeling_data2vec_audio.Data2VecAudioPreTrainedModel',
        'transformers.models.data2vec.modeling_data2vec_text.Data2VecTextModel',
        'transformers.models.data2vec.modeling_data2vec_text.Data2VecTextPreTrainedModel',
        'transformers.models.data2vec.modeling_data2vec_vision.Data2VecVisionModel',
        'transformers.models.data2vec.modeling_data2vec_vision.Data2VecVisionPreTrainedModel',
        'transformers.models.deberta.modeling_deberta.DebertaModel',
        'transformers.models.deberta.modeling_deberta.DebertaPreTrainedModel',
        'transformers.models.deberta_v2.modeling_deberta_v2.DebertaV2Model',
        'transformers.models.deberta_v2.modeling_deberta_v2.DebertaV2PreTrainedModel',
        'transformers.models.decision_transformer.modeling_decision_transformer.DecisionTransformerGPT2Model',
        'transformers.models.decision_transformer.modeling_decision_transformer.DecisionTransformerGPT2PreTrainedModel',
        'transformers.models.decision_transformer.modeling_decision_transformer.DecisionTransformerModel',
        'transformers.models.decision_transformer.modeling_decision_transformer.DecisionTransformerPreTrainedModel',
        'transformers.models.deit.modeling_deit.DeiTModel',
        'transformers.models.deit.modeling_deit.DeiTPreTrainedModel',
        'transformers.models.distilbert.modeling_distilbert.DistilBertModel',
        'transformers.models.distilbert.modeling_distilbert.DistilBertPreTrainedModel',
        'transformers.models.donut.modeling_donut_swin.DonutSwinModel',
        'transformers.models.donut.modeling_donut_swin.DonutSwinPreTrainedModel',
        'transformers.models.dpr.modeling_dpr.DPRPreTrainedModel',
        'transformers.models.dpt.modeling_dpt.DPTModel',
        'transformers.models.dpt.modeling_dpt.DPTPreTrainedModel',
        'transformers.models.electra.modeling_electra.ElectraModel',
        'transformers.models.electra.modeling_electra.ElectraPreTrainedModel',
        'transformers.models.encoder_decoder.modeling_encoder_decoder.EncoderDecoderModel',
        'transformers.models.ernie.modeling_ernie.ErnieModel',
        'transformers.models.ernie.modeling_ernie.ErniePreTrainedModel',
        'transformers.models.flaubert.modeling_flaubert.FlaubertModel',
        'transformers.models.flaubert.modeling_flaubert.FlaubertWithLMHeadModel',
        'transformers.models.xlm.modeling_xlm.XLMModel',
        'transformers.models.xlm.modeling_xlm.XLMWithLMHeadModel',
        'transformers.models.flava.modeling_flava.FlavaImageModel',
        'transformers.models.flava.modeling_flava.FlavaModel',
        'transformers.models.flava.modeling_flava.FlavaMultimodalModel',
        'transformers.models.flava.modeling_flava.FlavaPreTrainedModel',
        'transformers.models.flava.modeling_flava.FlavaTextModel',
        'transformers.models.fnet.modeling_fnet.FNetModel',
        'transformers.models.fnet.modeling_fnet.FNetPreTrainedModel',
        'transformers.models.fsmt.modeling_fsmt.FSMTModel',
        'transformers.models.fsmt.modeling_fsmt.PretrainedFSMTModel',
        'transformers.models.funnel.modeling_funnel.FunnelBaseModel',
        'transformers.models.funnel.modeling_funnel.FunnelModel',
        'transformers.models.funnel.modeling_funnel.FunnelPreTrainedModel',
        'transformers.models.glpn.modeling_glpn.GLPNModel',
        'transformers.models.glpn.modeling_glpn.GLPNPreTrainedModel',
        'transformers.models.gpt2.modeling_gpt2.GPT2DoubleHeadsModel',
        'transformers.models.gpt2.modeling_gpt2.GPT2LMHeadModel',
        'transformers.models.gpt2.modeling_gpt2.GPT2Model',
        'transformers.models.gpt2.modeling_gpt2.GPT2PreTrainedModel',
        'transformers.models.gpt_neo.modeling_gpt_neo.GPTNeoModel',
        'transformers.models.gpt_neo.modeling_gpt_neo.GPTNeoPreTrainedModel',
        'transformers.models.gpt_neox.modeling_gpt_neox.GPTNeoXModel',
        'transformers.models.gpt_neox.modeling_gpt_neox.GPTNeoXPreTrainedModel',
        'transformers.models.gptj.modeling_gptj.GPTJModel',
        'transformers.models.gptj.modeling_gptj.GPTJPreTrainedModel',
        'transformers.models.groupvit.modeling_groupvit.GroupViTModel',
        'transformers.models.groupvit.modeling_groupvit.GroupViTPreTrainedModel',
        'transformers.models.groupvit.modeling_groupvit.GroupViTTextModel',
        'transformers.models.groupvit.modeling_groupvit.GroupViTVisionModel',
        'transformers.models.hubert.modeling_hubert.HubertModel',
        'transformers.models.hubert.modeling_hubert.HubertPreTrainedModel',
        'transformers.models.ibert.modeling_ibert.IBertModel',
        'transformers.models.ibert.modeling_ibert.IBertPreTrainedModel',
        'transformers.models.imagegpt.modeling_imagegpt.ImageGPTModel',
        'transformers.models.imagegpt.modeling_imagegpt.ImageGPTPreTrainedModel',
        'transformers.models.layoutlm.modeling_layoutlm.LayoutLMModel',
        'transformers.models.layoutlm.modeling_layoutlm.LayoutLMPreTrainedModel',
        'transformers.models.layoutlmv2.modeling_layoutlmv2.LayoutLMv2Model',
        'transformers.models.layoutlmv2.modeling_layoutlmv2.LayoutLMv2PreTrainedModel',
        'transformers.models.layoutlmv3.modeling_layoutlmv3.LayoutLMv3Model',
        'transformers.models.layoutlmv3.modeling_layoutlmv3.LayoutLMv3PreTrainedModel',
        'transformers.models.led.modeling_led.LEDModel',
        'transformers.models.led.modeling_led.LEDPreTrainedModel',
        'transformers.models.levit.modeling_levit.LevitModel',
        'transformers.models.levit.modeling_levit.LevitPreTrainedModel',
        'transformers.models.longformer.modeling_longformer.LongformerModel',
        'transformers.models.longformer.modeling_longformer.LongformerPreTrainedModel',
        'transformers.models.longt5.modeling_longt5.LongT5EncoderModel',
        'transformers.models.longt5.modeling_longt5.LongT5Model',
        'transformers.models.longt5.modeling_longt5.LongT5PreTrainedModel',
        'transformers.models.luke.modeling_luke.LukeModel',
        'transformers.models.luke.modeling_luke.LukePreTrainedModel',
        'transformers.models.lxmert.modeling_lxmert.LxmertModel',
        'transformers.models.lxmert.modeling_lxmert.LxmertPreTrainedModel',
        'transformers.models.m2m_100.modeling_m2m_100.M2M100Model',
        'transformers.models.m2m_100.modeling_m2m_100.M2M100PreTrainedModel',
        'transformers.models.marian.modeling_marian.MarianMTModel',
        'transformers.models.marian.modeling_marian.MarianModel',
        'transformers.models.marian.modeling_marian.MarianPreTrainedModel',
        'transformers.models.maskformer.modeling_maskformer.MaskFormerModel',
        'transformers.models.maskformer.modeling_maskformer.MaskFormerPreTrainedModel',
        'transformers.models.maskformer.modeling_maskformer.MaskFormerFPNModel',
        'transformers.models.maskformer.modeling_maskformer.MaskFormerSwinModel',
        'transformers.models.mbart.modeling_mbart.MBartModel',
        'transformers.models.mbart.modeling_mbart.MBartPreTrainedModel',
        'transformers.models.mctct.modeling_mctct.MCTCTModel',
        'transformers.models.mctct.modeling_mctct.MCTCTPreTrainedModel',
        'transformers.models.megatron_bert.modeling_megatron_bert.MegatronBertModel',
        'transformers.models.megatron_bert.modeling_megatron_bert.MegatronBertPreTrainedModel',
        'transformers.models.mmbt.modeling_mmbt.MMBTModel',
        'transformers.models.mobilebert.modeling_mobilebert.MobileBertModel',
        'transformers.models.mobilebert.modeling_mobilebert.MobileBertPreTrainedModel',
        'transformers.models.mobilevit.modeling_mobilevit.MobileViTModel',
        'transformers.models.mobilevit.modeling_mobilevit.MobileViTPreTrainedModel',
        'transformers.models.mpnet.modeling_mpnet.MPNetModel',
        'transformers.models.mpnet.modeling_mpnet.MPNetPreTrainedModel',
        'transformers.models.mt5.modeling_mt5.MT5EncoderModel',
        'transformers.models.mt5.modeling_mt5.MT5Model',
        'transformers.models.t5.modeling_t5.T5EncoderModel',
        'transformers.models.t5.modeling_t5.T5Model',
        'transformers.models.mvp.modeling_mvp.MvpModel',
        'transformers.models.mvp.modeling_mvp.MvpPreTrainedModel',
        'transformers.models.nezha.modeling_nezha.NezhaModel',
        'transformers.models.nezha.modeling_nezha.NezhaPreTrainedModel',
        'transformers.models.nystromformer.modeling_nystromformer.NystromformerModel',
        'transformers.models.nystromformer.modeling_nystromformer.NystromformerPreTrainedModel',
        'transformers.models.openai.modeling_openai.OpenAIGPTDoubleHeadsModel',
        'transformers.models.openai.modeling_openai.OpenAIGPTLMHeadModel',
        'transformers.models.openai.modeling_openai.OpenAIGPTModel',
        'transformers.models.openai.modeling_openai.OpenAIGPTPreTrainedModel',
        'transformers.models.opt.modeling_opt.OPTModel',
        'transformers.models.opt.modeling_opt.OPTPreTrainedModel',
        'transformers.models.owlvit.modeling_owlvit.OwlViTModel',
        'transformers.models.owlvit.modeling_owlvit.OwlViTPreTrainedModel',
        'transformers.models.owlvit.modeling_owlvit.OwlViTTextModel',
        'transformers.models.owlvit.modeling_owlvit.OwlViTVisionModel',
        'transformers.models.pegasus.modeling_pegasus.PegasusModel',
        'transformers.models.pegasus.modeling_pegasus.PegasusPreTrainedModel',
        'transformers.models.pegasus_x.modeling_pegasus_x.PegasusXModel',
        'transformers.models.pegasus_x.modeling_pegasus_x.PegasusXPreTrainedModel',
        'transformers.models.perceiver.modeling_perceiver.PerceiverModel',
        'transformers.models.perceiver.modeling_perceiver.PerceiverPreTrainedModel',
        'transformers.models.plbart.modeling_plbart.PLBartModel',
        'transformers.models.plbart.modeling_plbart.PLBartPreTrainedModel',
        'transformers.models.poolformer.modeling_poolformer.PoolFormerModel',
        'transformers.models.poolformer.modeling_poolformer.PoolFormerPreTrainedModel',
        'transformers.models.prophetnet.modeling_prophetnet.ProphetNetModel',
        'transformers.models.prophetnet.modeling_prophetnet.ProphetNetPreTrainedModel',
        'transformers.models.qdqbert.modeling_qdqbert.QDQBertLMHeadModel',
        'transformers.models.qdqbert.modeling_qdqbert.QDQBertModel',
        'transformers.models.qdqbert.modeling_qdqbert.QDQBertPreTrainedModel',
        'transformers.models.rag.modeling_rag.RagModel',
        'transformers.models.rag.modeling_rag.RagPreTrainedModel',
        'transformers.models.realm.modeling_realm.RealmPreTrainedModel',
        'transformers.models.realm.modeling_realm.RealmBertModel',
        'transformers.models.reformer.modeling_reformer.ReformerModel',
        'transformers.models.reformer.modeling_reformer.ReformerPreTrainedModel',
        'transformers.models.regnet.modeling_regnet.RegNetModel',
        'transformers.models.regnet.modeling_regnet.RegNetPreTrainedModel',
        'transformers.models.rembert.modeling_rembert.RemBertModel',
        'transformers.models.rembert.modeling_rembert.RemBertPreTrainedModel',
        'transformers.models.resnet.modeling_resnet.ResNetModel',
        'transformers.models.resnet.modeling_resnet.ResNetPreTrainedModel',
        'transformers.models.retribert.modeling_retribert.RetriBertModel',
        'transformers.models.retribert.modeling_retribert.RetriBertPreTrainedModel',
        'transformers.models.roberta.modeling_roberta.RobertaPreTrainedModel',
        'transformers.models.roformer.modeling_roformer.RoFormerModel',
        'transformers.models.roformer.modeling_roformer.RoFormerPreTrainedModel',
        'transformers.models.segformer.modeling_segformer.SegformerModel',
        'transformers.models.segformer.modeling_segformer.SegformerPreTrainedModel',
        'transformers.models.sew.modeling_sew.SEWModel',
        'transformers.models.sew.modeling_sew.SEWPreTrainedModel',
        'transformers.models.sew_d.modeling_sew_d.SEWDModel',
        'transformers.models.sew_d.modeling_sew_d.SEWDPreTrainedModel',
        'transformers.models.speech_encoder_decoder.modeling_speech_encoder_decoder.SpeechEncoderDecoderModel',
        'transformers.models.speech_to_text.modeling_speech_to_text.Speech2TextModel',
        'transformers.models.speech_to_text.modeling_speech_to_text.Speech2TextPreTrainedModel',
        'transformers.models.speech_to_text_2.modeling_speech_to_text_2.Speech2Text2PreTrainedModel',
        'transformers.models.splinter.modeling_splinter.SplinterModel',
        'transformers.models.splinter.modeling_splinter.SplinterPreTrainedModel',
        'transformers.models.squeezebert.modeling_squeezebert.SqueezeBertModel',
        'transformers.models.squeezebert.modeling_squeezebert.SqueezeBertPreTrainedModel',
        'transformers.models.swin.modeling_swin.SwinModel',
        'transformers.models.swin.modeling_swin.SwinPreTrainedModel',
        'transformers.models.swinv2.modeling_swinv2.Swinv2Model',
        'transformers.models.swinv2.modeling_swinv2.Swinv2PreTrainedModel',
        'transformers.models.t5.modeling_t5.T5PreTrainedModel',
        'transformers.models.tapas.modeling_tapas.TapasModel',
        'transformers.models.tapas.modeling_tapas.TapasPreTrainedModel',
        'transformers.models.trajectory_transformer.modeling_trajectory_transformer.TrajectoryTransformerModel',
        'transformers.models.trajectory_transformer.modeling_trajectory_transformer.TrajectoryTransformerPreTrainedModel',
        'transformers.models.transfo_xl.modeling_transfo_xl.TransfoXLLMHeadModel',
        'transformers.models.transfo_xl.modeling_transfo_xl.TransfoXLModel',
        'transformers.models.transfo_xl.modeling_transfo_xl.TransfoXLPreTrainedModel',
        'transformers.models.trocr.modeling_trocr.TrOCRPreTrainedModel',
        'transformers.models.unispeech.modeling_unispeech.UniSpeechModel',
        'transformers.models.unispeech.modeling_unispeech.UniSpeechPreTrainedModel',
        'transformers.models.unispeech_sat.modeling_unispeech_sat.UniSpeechSatModel',
        'transformers.models.unispeech_sat.modeling_unispeech_sat.UniSpeechSatPreTrainedModel',
        'transformers.models.van.modeling_van.VanModel',
        'transformers.models.van.modeling_van.VanPreTrainedModel',
        'transformers.models.videomae.modeling_videomae.VideoMAEModel',
        'transformers.models.videomae.modeling_videomae.VideoMAEPreTrainedModel',
        'transformers.models.vilt.modeling_vilt.ViltModel',
        'transformers.models.vilt.modeling_vilt.ViltPreTrainedModel',
        'transformers.models.vision_encoder_decoder.modeling_vision_encoder_decoder.VisionEncoderDecoderModel',
        'transformers.models.vision_text_dual_encoder.modeling_vision_text_dual_encoder.VisionTextDualEncoderModel',
        'transformers.models.visual_bert.modeling_visual_bert.VisualBertModel',
        'transformers.models.visual_bert.modeling_visual_bert.VisualBertPreTrainedModel',
        'transformers.models.vit.modeling_vit.ViTModel',
        'transformers.models.vit.modeling_vit.ViTPreTrainedModel',
        'transformers.models.vit_mae.modeling_vit_mae.ViTMAEModel',
        'transformers.models.vit_mae.modeling_vit_mae.ViTMAEPreTrainedModel',
        'transformers.models.wav2vec2.modeling_wav2vec2.Wav2Vec2Model',
        'transformers.models.wav2vec2.modeling_wav2vec2.Wav2Vec2PreTrainedModel',
        'transformers.models.wav2vec2_conformer.modeling_wav2vec2_conformer.Wav2Vec2ConformerModel',
        'transformers.models.wav2vec2_conformer.modeling_wav2vec2_conformer.Wav2Vec2ConformerPreTrainedModel',
        'transformers.models.wavlm.modeling_wavlm.WavLMModel',
        'transformers.models.wavlm.modeling_wavlm.WavLMPreTrainedModel',
        'transformers.models.x_clip.modeling_x_clip.XCLIPModel',
        'transformers.models.x_clip.modeling_x_clip.XCLIPPreTrainedModel',
        'transformers.models.x_clip.modeling_x_clip.XCLIPTextModel',
        'transformers.models.x_clip.modeling_x_clip.XCLIPVisionModel',
        'transformers.models.xglm.modeling_xglm.XGLMModel',
        'transformers.models.xglm.modeling_xglm.XGLMPreTrainedModel',
        'transformers.models.xlm.modeling_xlm.XLMPreTrainedModel',
        'transformers.models.xlm_prophetnet.modeling_xlm_prophetnet.XLMProphetNetModel',
        'transformers.models.xlm_roberta.modeling_xlm_roberta.XLMRobertaModel',
        'transformers.models.xlm_roberta_xl.modeling_xlm_roberta_xl.XLMRobertaXLModel',
        'transformers.models.xlm_roberta_xl.modeling_xlm_roberta_xl.XLMRobertaXLPreTrainedModel',
        'transformers.models.xlnet.modeling_xlnet.XLNetLMHeadModel',
        'transformers.models.xlnet.modeling_xlnet.XLNetModel',
        'transformers.models.xlnet.modeling_xlnet.XLNetPreTrainedModel',
        'transformers.models.yolos.modeling_yolos.YolosModel',
        'transformers.models.yolos.modeling_yolos.YolosPreTrainedModel',
        'transformers.models.yoso.modeling_yoso.YosoModel',
        'transformers.models.yoso.modeling_yoso.YosoPreTrainedModel'
    ),
    help_info=HelpInfo(
        imports="transformers",
        parameter_deps={"huggingface_model_name": PHugsModelName},
        definition=[
            "huggingface_model_base = transformers.AutoModelForSequenceClassification.from_pretrained({huggingface_model_name})"
        ],
        args_map={"model": "huggingface_model_base"}
    )
)

# Huggingface sequence classifiers.
# Output of:
# print(concretize(
#    transformers.models, pattern=re.compile(r"transformers\..+ForSequenceClassification")
# ))
TModelHugsClassifier = Union(
    'transformers.models.albert.modeling_albert.AlbertForSequenceClassification',
    'transformers.models.albert.modeling_tf_albert.TFAlbertForSequenceClassification',
    # 'transformers.models.auto.modeling_auto.AutoModelForSequenceClassification',
    # 'transformers.models.auto.modeling_tf_auto.TFAutoModelForSequenceClassification',
    # NOTE(piotrm): The above "auto" classes are not models themselves.
    'transformers.models.bart.modeling_bart.BartForSequenceClassification',
    'transformers.models.bert.modeling_bert.BertForSequenceClassification',
    'transformers.models.bert.modeling_tf_bert.TFBertForSequenceClassification',
    'transformers.models.big_bird.modeling_big_bird.BigBirdForSequenceClassification',
    'transformers.models.bigbird_pegasus.modeling_bigbird_pegasus.BigBirdPegasusForSequenceClassification',
    'transformers.models.bloom.modeling_bloom.BloomForSequenceClassification',
    'transformers.models.camembert.modeling_camembert.CamembertForSequenceClassification',
    'transformers.models.camembert.modeling_tf_camembert.TFCamembertForSequenceClassification',
    'transformers.models.canine.modeling_canine.CanineForSequenceClassification',
    'transformers.models.convbert.modeling_convbert.ConvBertForSequenceClassification',
    'transformers.models.convbert.modeling_tf_convbert.TFConvBertForSequenceClassification',
    'transformers.models.ctrl.modeling_ctrl.CTRLForSequenceClassification',
    'transformers.models.ctrl.modeling_tf_ctrl.TFCTRLForSequenceClassification',
    'transformers.models.data2vec.modeling_data2vec_audio.Data2VecAudioForSequenceClassification',
    'transformers.models.data2vec.modeling_data2vec_text.Data2VecTextForSequenceClassification',
    'transformers.models.deberta.modeling_deberta.DebertaForSequenceClassification',
    'transformers.models.deberta.modeling_tf_deberta.TFDebertaForSequenceClassification',
    'transformers.models.deberta_v2.modeling_deberta_v2.DebertaV2ForSequenceClassification',
    'transformers.models.deberta_v2.modeling_tf_deberta_v2.TFDebertaV2ForSequenceClassification',
    'transformers.models.distilbert.modeling_distilbert.DistilBertForSequenceClassification',
    'transformers.models.distilbert.modeling_tf_distilbert.TFDistilBertForSequenceClassification',
    'transformers.models.electra.modeling_electra.ElectraForSequenceClassification',
    'transformers.models.electra.modeling_tf_electra.TFElectraForSequenceClassification',
    'transformers.models.ernie.modeling_ernie.ErnieForSequenceClassification',
    'transformers.models.esm.modeling_esm.EsmForSequenceClassification',
    'transformers.models.flaubert.modeling_flaubert.FlaubertForSequenceClassification',
    'transformers.models.flaubert.modeling_tf_flaubert.TFFlaubertForSequenceClassification',
    'transformers.models.xlm.modeling_xlm.XLMForSequenceClassification',
    'transformers.models.xlm.modeling_tf_xlm.TFXLMForSequenceClassification',
    'transformers.models.fnet.modeling_fnet.FNetForSequenceClassification',
    'transformers.models.funnel.modeling_funnel.FunnelForSequenceClassification',
    'transformers.models.funnel.modeling_tf_funnel.TFFunnelForSequenceClassification',
    'transformers.models.gpt2.modeling_gpt2.GPT2ForSequenceClassification',
    'transformers.models.gpt2.modeling_tf_gpt2.TFGPT2ForSequenceClassification',
    'transformers.models.gpt_neo.modeling_gpt_neo.GPTNeoForSequenceClassification',
    'transformers.models.gptj.modeling_gptj.GPTJForSequenceClassification',
    'transformers.models.gptj.modeling_tf_gptj.TFGPTJForSequenceClassification',
    'transformers.models.hubert.modeling_hubert.HubertForSequenceClassification',
    'transformers.models.ibert.modeling_ibert.IBertForSequenceClassification',
    'transformers.models.layoutlm.modeling_layoutlm.LayoutLMForSequenceClassification',
    'transformers.models.layoutlm.modeling_tf_layoutlm.TFLayoutLMForSequenceClassification',
    'transformers.models.layoutlmv2.modeling_layoutlmv2.LayoutLMv2ForSequenceClassification',
    'transformers.models.layoutlmv3.modeling_layoutlmv3.LayoutLMv3ForSequenceClassification',
    'transformers.models.layoutlmv3.modeling_tf_layoutlmv3.TFLayoutLMv3ForSequenceClassification',
    'transformers.models.led.modeling_led.LEDForSequenceClassification',
    'transformers.models.longformer.modeling_longformer.LongformerForSequenceClassification',
    'transformers.models.longformer.modeling_tf_longformer.TFLongformerForSequenceClassification',
    'transformers.models.luke.modeling_luke.LukeForSequenceClassification',
    'transformers.models.markuplm.modeling_markuplm.MarkupLMForSequenceClassification',
    'transformers.models.mbart.modeling_mbart.MBartForSequenceClassification',
    'transformers.models.megatron_bert.modeling_megatron_bert.MegatronBertForSequenceClassification',
    'transformers.models.mobilebert.modeling_mobilebert.MobileBertForSequenceClassification',
    'transformers.models.mobilebert.modeling_tf_mobilebert.TFMobileBertForSequenceClassification',
    'transformers.models.mpnet.modeling_mpnet.MPNetForSequenceClassification',
    'transformers.models.mpnet.modeling_tf_mpnet.TFMPNetForSequenceClassification',
    'transformers.models.mvp.modeling_mvp.MvpForSequenceClassification',
    'transformers.models.nezha.modeling_nezha.NezhaForSequenceClassification',
    'transformers.models.nystromformer.modeling_nystromformer.NystromformerForSequenceClassification',
    'transformers.models.openai.modeling_openai.OpenAIGPTForSequenceClassification',
    'transformers.models.openai.modeling_tf_openai.TFOpenAIGPTForSequenceClassification',
    'transformers.models.opt.modeling_opt.OPTForSequenceClassification',
    'transformers.models.perceiver.modeling_perceiver.PerceiverForSequenceClassification',
    'transformers.models.plbart.modeling_plbart.PLBartForSequenceClassification',
    'transformers.models.qdqbert.modeling_qdqbert.QDQBertForSequenceClassification',
    'transformers.models.reformer.modeling_reformer.ReformerForSequenceClassification',
    'transformers.models.rembert.modeling_rembert.RemBertForSequenceClassification',
    'transformers.models.rembert.modeling_tf_rembert.TFRemBertForSequenceClassification',
    'transformers.models.roberta.modeling_roberta.RobertaForSequenceClassification',
    'transformers.models.roberta.modeling_tf_roberta.TFRobertaForSequenceClassification',
    'transformers.models.roformer.modeling_roformer.RoFormerForSequenceClassification',
    'transformers.models.roformer.modeling_tf_roformer.TFRoFormerForSequenceClassification',
    'transformers.models.sew.modeling_sew.SEWForSequenceClassification',
    'transformers.models.sew_d.modeling_sew_d.SEWDForSequenceClassification',
    'transformers.models.squeezebert.modeling_squeezebert.SqueezeBertForSequenceClassification',
    'transformers.models.tapas.modeling_tf_tapas.TFTapasForSequenceClassification',
    'transformers.models.tapas.modeling_tapas.TapasForSequenceClassification',
    'transformers.models.transfo_xl.modeling_tf_transfo_xl.TFTransfoXLForSequenceClassification',
    'transformers.models.transfo_xl.modeling_transfo_xl.TransfoXLForSequenceClassification',
    'transformers.models.unispeech.modeling_unispeech.UniSpeechForSequenceClassification',
    'transformers.models.unispeech_sat.modeling_unispeech_sat.UniSpeechSatForSequenceClassification',
    'transformers.models.wav2vec2.modeling_wav2vec2.Wav2Vec2ForSequenceClassification',
    'transformers.models.wav2vec2_conformer.modeling_wav2vec2_conformer.Wav2Vec2ConformerForSequenceClassification',
    'transformers.models.wavlm.modeling_wavlm.WavLMForSequenceClassification',
    'transformers.models.xlm_roberta.modeling_tf_xlm_roberta.TFXLMRobertaForSequenceClassification',
    'transformers.models.xlm_roberta.modeling_xlm_roberta.XLMRobertaForSequenceClassification',
    'transformers.models.xlm_roberta_xl.modeling_xlm_roberta_xl.XLMRobertaXLForSequenceClassification',
    'transformers.models.xlnet.modeling_tf_xlnet.TFXLNetForSequenceClassification',
    'transformers.models.xlnet.modeling_xlnet.XLNetForSequenceClassification',
    'transformers.models.yoso.modeling_yoso.YosoForSequenceClassification'
)

PModelHugsClassifier = Parameter(
    "model_hugs_classifier",
    typ=Intersection(PModel, TModelHugsClassifier),
    desc=""
)

# Huggingface audio sequence classifiers
TModelHugsAudioClassifierPattern = TypeMatching(
    pattern=
    "transformers\..+(UniSpeech|Audio|WavLM|Wav2Vec2).*ForSequenceClassification"
)
# print(concretize(
#    transformers.models,
#    TModelHugsAudioClassifierPattern
# ))
TModelHugsAudioClassifier = Union(
    'transformers.models.data2vec.modeling_data2vec_audio.Data2VecAudioForSequenceClassification',
    'transformers.models.unispeech.modeling_unispeech.UniSpeechForSequenceClassification',
    'transformers.models.unispeech_sat.modeling_unispeech_sat.UniSpeechSatForSequenceClassification',
    'transformers.models.wav2vec2.modeling_wav2vec2.Wav2Vec2ForSequenceClassification',
    'transformers.models.wav2vec2_conformer.modeling_wav2vec2_conformer.Wav2Vec2ConformerForSequenceClassification',
    'transformers.models.wavlm.modeling_wavlm.WavLMForSequenceClassification'
)

PModelHugsAudioClassifier = Parameter(
    "model_hugs_audio_classifier",
    typ=Intersection(PModel, TModelHugsAudioClassifier),
    desc="Audio classifier. These are not yet supperted.",
    help_info=HelpInfo(
        imports="transformers",
        definition=[
            "model_hugs_audio_classifier = transformers.Data2VecAudioForSequenceClassification.from_pretrained('hf-internal-testing/tiny-random-data2vec-seq-class')"
        ],
        args_map={"model": "model_hugs_audio_classifier"}
    )
)

# Huggingface text sequence classifiers. NOTE(piotrm): Not using the "Not" type
# constructor here intentionally as doing so requires enabling very slow
# subclass checking.
PModelHugsTextClassifier = Parameter(
    "model_hugs_text_classifier",
    typ=Union(
        *(
            t for t in TModelHugsClassifier.types
            if t not in TModelHugsAudioClassifier.types
        )
    ),
    desc="A Huggingface Text Sequence Classifier object",
    help_info=HelpInfo(
        imports="transformers",
        parameter_deps={"huggingface_model_name": PHugsModelName},
        definition=[
            "model_hugs_text_classifier = transformers.AutoModelForSequenceClassification.from_pretrained({huggingface_model_name})"
        ],
        args_map={"model": "model_hugs_text_classifier"}
    )
)

# Huggingface (text?) tokenizers
TTokenizerHugs = Union(
    'transformers.PreTrainedTokenizer', 'transformers.PreTrainedTokenizerFast'
)
TKerasTextVectorizationTokenizer = "tensorflow.keras.layers.TextVectorization"
TTFTextTokenizer = "tensorflow_text.Tokenizer"
TTFTextTokenizerWithOffsets = "tensorflow_text.TokenizerWithOffsets"
TTFTextBertTokenizer = "tensorflow_text.BertTokenizer"

TTF2Tokenizer = Union(
    TKerasTextVectorizationTokenizer, TTFTextTokenizer,
    TTFTextTokenizerWithOffsets, TTFTextBertTokenizer, TTF2Model
)


def example_tokenizer(*args, **kwargs) -> Any:
    ...


TBlackboxTokenizer = Function(inspect.signature(example_tokenizer))

PTokenizerHugs = Parameter(
    "tokenizer_hugs",
    typ=TTokenizerHugs,
    desc="Huggingface Tokenizer",
    help_info=HelpInfo(
        imports="transformers",
        parameter_deps={"huggingface_model_name": PHugsModelName},
        definition=[
            "tokenizer_hugs = transformers.AutoTokenizer.from_pretrained({huggingface_model_name})"
        ],
        args_map={"model": "tokenizer_hugs"}
    )
)

PTokenWordPrefix = Parameter(
    "token_word_prefix",
    typ=str,
    desc=
    "Prefix of tokens that indicates they follow a whitespace. Typical examples include 'Ġ' and '##'."
)

PKerasTextVectorizationTokenizer = Parameter(
    "tokenizer_kerastext",
    typ=TKerasTextVectorizationTokenizer,
    desc="A tf.keras.layers.TextVectorization Tokenizer object.",
    help_info=HelpInfo(
        imports="tensorflow as tf",
        definition=[
            "tokenizer_kerastext = tf.keras.layers.TextVectorization(split='whitespace', max_tokens=20, output_mode='int')"
        ],
        args_map={"model": "tokenizer_kerastext"}
    )
)

PTFTextTokenizer = Parameter(
    "tokenizer_tftext",
    typ=TTFTextTokenizer,
    desc="",
    help_info=HelpInfo(
        imports=["tensorflow as tf", "tensorflow_text as text"],
        parameter_deps={"vocab": PVocab},
        definition=[
            inspect.cleandoc(
                """
            lookup_table = tf.lookup.StaticVocabularyTable(
                tf.lookup.KeyValueTensorInitializer(
                    keys=list(vocab.keys()),
                    key_dtype=tf.string,
                    values=tf.range(tf.size(list(vocab.keys()), out_type=tf.int64), dtype=tf.int64), 
                    value_dtype=tf.int64
                ),
                num_oov_buckets=1
            )
            """
            ), "tokenizer_tftext = text.BertTokenizer('en_vocab.txt')"
        ],
        args_map={"model": "tokenizer_tftext"}
    )
)

PTFTextTokenizerWithOffsets = Parameter(
    "tokenizer_tftext_offsets", typ=TTFTextTokenizerWithOffsets, desc=""
)

PTF2Tokenizer = Parameter(
    "tokenizer_tf2",
    typ=TTF2Tokenizer,
    desc="Tensorflow 2 Tokenizer",
    help_info=HelpInfo(
        imports=["tensorflow as tf", "tensorflow_hub as hub"],
        definition=[
            "tfhub_handle_preprocess = 'https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3'",
            "text_input = tf.keras.layers.Input(shape=(), dtype=tf.string, name='text')",
            "tokenize = hub.KerasLayer(tfhub_handle_preprocess)",
            "encoder_inputs = tokenize(text_input)",
            "tokenizer_tf2 = tf.keras.Model(text_input, encoder_inputs)",
        ],
        args_map={"model": "tokenizer_tf2"}
    )
)

PBlackboxTokenizer = Parameter(
    "tokenizer_blackbox", typ=TBlackboxTokenizer, desc=""
)

PTokenizer = Parameter(
    "tokenizer",
    typ=Union(TTokenizerHugs, TTF2Tokenizer, TBlackboxTokenizer),
    desc="A general Tokenizer object.",
    help_info=PTokenizerHugs.help_info
)
"""
# TODO: move to testing
assert issubclass(transformers.models.albert.modeling_albert.AlbertForSequenceClassification, PModelHugsClassifier) == True
assert issubclass(transformers.models.albert.modeling_albert.AlbertForSequenceClassification, PModelHugsAudioClassifier) == False
assert issubclass(transformers.models.albert.modeling_albert.AlbertForSequenceClassification, PModelHugsTextClassifier) == True
assert issubclass(transformers.models.albert.modeling_albert.AlbertForSequenceClassification, PModel) == True
assert issubclass(transformers.models.albert.modeling_albert.AlbertForSequenceClassification, PModelTorch) == True
assert issubclass(transformers.models.albert.modeling_albert.AlbertForSequenceClassification, PModelTF1) == False
"""

# Huggingface text classifiers in the pytorch api
PModelTorchHugsTextClassifier = Parameter(
    "model_torch_hugs_text_classifier",
    typ=Intersection(TTorchModel, PModelHugsTextClassifier),
    desc=""
)

# Huggingface text classifiers in the tensorflow api
PModelTFHugsTextClassifier = Parameter(
    "model_tf_hugs_text_classifier",
    typ=Intersection(TTF2Model, PModelHugsTextClassifier),
    desc=""
)

PModelName = Parameter(
    "model_name",
    desc="The model name for a managed truera workspace.",
    help_info=HelpInfo(
        definition=["model_name = 'my_model' # TODO: Replace me"],
        args_map={"model_name": "model_name"}
    ),
    typ=str
)

PProjectName = Parameter(
    "project_name",
    desc="Project name for managed truera workspace.",
    typ=str,
    help_info=HelpInfo(
        definition=["project_name = 'my_project' # TODO: Replace me"],
        args_map={"project_name": "project_name"}
    )
)

PDataSplitName = Parameter(
    "data_split_name",
    desc="Data split name for managed truera workspace.",
    typ=str,
    help_info=HelpInfo(
        definition=["data_split_name = 'my_data_split' # TODO: Replace me"],
        args_map={"data_split_name": "data_split_name"}
    )
)

PDataCollectionName = Parameter(
    "data_collection_name",
    desc="Data collection name for managed truera workspace.",
    typ=str,
    help_info=HelpInfo(
        definition=[
            "data_collection_name = 'my_data_collection' # TODO: Replace me"
        ],
        args_map={"data_collection_name": "data_collection_name"}
    )
)


# Here only for its signature:
def example_get_model(path: Path) -> PModel:
    ...


PGetModel = Parameter(
    "get_model",
    desc=(
        "Function to retrieve model given a path."  #TODO: More details here.
    ),
    typ=Function(inspect.signature(example_get_model)),
    help_info=HelpInfo(
        imports="from pathlib import Path",
        definition=[
            inspect.cleandoc(
                """
            def get_model(path: Path):
                # load model from path
                model = load_model_from_path(path) 
                return model
            """
            )
        ],
        args_map={"get_model": "get_model"}
    )
)


# Here only for its signature:
def example_eval_model(
    model: PModel, args: Tuple[Any], kwargs: Dict[str, Any]
) -> Any:
    ...


PEvalModel = Parameter(
    "eval_model",
    desc=
    "Function to evalate a model and return outputs from one forward pass.",  #TODO: More details here.
    typ=Function(inspect.signature(example_eval_model)),
    help_info=HelpInfo(
        imports=[
            "typing.Tuple", "typing.Dict", "typing.Any", "typing.Callable"
        ],
        definition=[
            inspect.cleandoc(
                """
            def eval_model(model: Callable, args: Tuple[Any], kwargs: Dict[str, Any]):
                # evaluate model
                outputs = model(*args, **kwargs)
                # output postprocessing here
                return outputs
            """
            )
        ],
        args_map={"eval_model": "eval_model"}
    )
)


# Here only for its signature:
def example_text_to_inputs(texts: Iterable[str]) -> Dict[str, Any]:
    ...


PTextToInputs = Parameter(
    "text_to_inputs",
    desc="Function to convert text to model evaluation inputs.",
    typ=Function(inspect.signature(example_text_to_inputs)),
    help_info=HelpInfo(
        definition=[
            inspect.cleandoc(
                """
            def text_to_inputs(texts: Iterable[str]):
                # convert texts to model inputs
                inputs = tokenize_text_to_model_input(texts) 
                return inputs
            """
            )
        ],
        args_map={"text_to_inputs": "text_to_inputs"}
    )
)


# Here only for its signature:
def example_text_to_token_ids(
    texts: Iterable[str]
) -> Iterable[Tuple[int, int]]:
    ...


PTextToTokenIds = Parameter(
    "text_to_token_ids",
    desc=
    "A function that converts batches of text to batches of lists of token ids.",
    typ=Function(inspect.signature(example_text_to_token_ids)),
    help_info=HelpInfo(
        imports=["typing.Iterable"],
        definition=[
            inspect.cleandoc(
                """
            # convert texts to token ids
            def text_to_token_ids(texts: Iterable[str]) -> Iterable[Iterable[int]]:
                # TODO: Implement this using your tokenizer
                token_ids = tokenize_text_to_token_ids(texts)
                return token_ids
            """
            ),
        ],
        args_map={"text_to_token_ids": "text_to_token_ids"}
    )
)


# Here only for its signature:
def example_text_to_spans(texts: Iterable[str]) -> Iterable[NLP.Types.Span]:
    ...


PTextToSpans = Parameter(
    "text_to_spans",
    desc=
    "Function to convert batches of text to an array of token offset spans.",
    typ=Function(inspect.signature(example_text_to_spans)),
    help_info=HelpInfo(
        imports=["numpy as np", "typing.List"],
        # parameter_deps={"tokenizer_hugs": PTokenizerHugs},
        definition=[
            inspect.cleandoc(
                """
            def text_to_spans(texts: List[str]) -> np.ndarray:
                parts = tokenizer.batch_encode_plus(
                    list(texts),
                    return_offsets_mapping=True,
                    return_tensors="np"
                )
                spans = parts['offset_mapping']
                return spans
            """
            )
        ],
        args_map={"text_to_spans": "text_to_spans"}
    )
)

PNEmbeddings = Parameter(
    "n_embeddings",
    desc="The number of dimensions in a token embedding vector.",
    typ=int,
    help_info=HelpInfo(
        definition=[
            "# n_embeddings represents the dimensionality of a token embedding vector",
            "n_embeddings = 768 # TODO: Replace me"
        ],
        args_map={"n_embeddings": "n_embeddings"}
    )
)

PNTokens = Parameter(
    "n_tokens",
    desc="The number of tokens accepted by a model.",
    typ=int,
    help_info=HelpInfo(
        definition=[
            "# n_tokens represents the number of tokens accepted by a model",
            "n_tokens = 20 # TODO: Replace me"
        ],
        args_map={"n_tokens": "n_tokens"}
    )
)

PDataInstance = Parameter(
    "data_instance",
    typ=str,
    desc="A single text instance.",
    help_info=HelpInfo(
        definition=[
            "# data_instance is a single text instance",
            "data_instance = 'this is a sample record' # TODO: Replace me"
        ],
        args_map={"data_instance": "data_instance"}
    )
)
PLabelInstance = Parameter(
    "label_instance",
    typ=int,
    desc="A single label instance.",
    help_info=HelpInfo(
        definition=[
            "# label_instance is a single label instance",
            "label_instance = 0 # TODO: Replace me"
        ],
        args_map={"label_instance": "label_instance"}
    )
)

# TODO(piotrm): prevent Sequence and Iterable from matching strings.
PDataSequence = Parameter(
    "data_sequence",
    typ=Sequence,
    desc="A sequence of text data.",
    help_info=HelpInfo(
        definition=[
            "# data_sequence represents a sequence of text data",
            "data_sequence = ['first input', 'second input'] # TODO: Replace me"
        ],
        args_map={"data_sequence": "data_sequence"}
    )
)

PLabelsSequence = Parameter(
    "labels_sequence",
    typ=Sequence,
    desc="A sequence of labels.",
    help_info=HelpInfo(
        definition=[
            "# labels_sequence represents a sequence of labels",
            "labels_sequence = [0, 1] # TODO: Replace me"
        ],
        args_map={"labels_sequence": "labels_sequence"}
    )
)

# TODO(piotrm): prevent Iterable from matching Sequence
PDataIterable = Parameter(
    "data_iterable",
    typ=Iterable,
    desc="An interable.",
    help_info=HelpInfo(
        definition=[
            "# data_iterable represents an iterable of text data",
            "data_iterable = iter(['first input', 'second input']) # TODO: Replace me"
        ],
        args_map={"data_iterable": "data_iterable"}
    )
)

PLabelsIterable = Parameter(
    "labels_iterable",
    typ=Iterable,
    desc="An interable of labels.",
    help_info=HelpInfo(
        definition=[
            "# labels_iterable represents an iterable of labels",
            "labels_iterable = iter([0, 1]) # TODO: Replace me"
        ],
        args_map={"labels_iterable": "labels_iterable"}
    )
)

# TODO(piotrm): prevent DataFrames/Series from matching any of the above.
PDataPandas = Parameter(
    "data_pandas",
    typ='pandas.DataFrame',
    desc="Pandas DataFrame.",
    help_info=HelpInfo(
        definition=[
            "# data_pandas represents a dataset in a pandas DataFrame",
            inspect.cleandoc(
                """
            data_pandas = pd.DataFrame({
                'text': ['first input', 'second input'], 
                'label': [0, 1], 
                'meta1': ['a', 'b'], 
                'meta2': [1, 2]
            })
            """
            )
        ],
        args_map={"data_pandas": "data_pandas"}
    )
)

PMetaPandas = Parameter(
    "meta_pandas",
    typ='pandas.DataFrame',
    desc="Metadata.",
    help_info=HelpInfo(
        definition=[
            "# meta_pandas represents metadata stored as a pandas DataFrame",
            "meta_pandas = pd.DataFrame({'meta1': ['a', 'b'], 'meta2': [1, 2]})"
        ],
        args_map={"meta_pandas": "meta_pandas"}
    )
)
"""
# more general handling of pytorch data in progress
PDataTorchDataset = Parameter(
    "data", typ='torch.utils.data.Dataset', desc="Torch dataset."
)
PDataTorchIterableDataset = Parameter(
    "data", typ='torch.utils.data.IterableDataset', desc="Torch iterable dataset."
)
PDataTorchDataLoaderRowwise = Parameter(
    "data", typ="torch.utils.data.DataLoader", desc="Torch data loader with a row-iterating dataset of map rows; i.e. DataLoader([dict(text='first input', label=0), ...])."
)
"""

PDataTorchColumnwise = Parameter(
    "data_torch_columnwise",
    typ=Mapping,
    desc=
    "Torch data with columns as a mapping; i.e. DataLoader(dict(text=['first input', 'second input'], label=[0, 1]))."
)
PDataTorchDataLoader = Parameter(
    "data_torch_dataloader",
    typ="torch.utils.data.DataLoader",
    desc="Torch data loader.",
    help_info=HelpInfo(
        imports="torch",
        definition=[
            inspect.cleandoc(
                """
            data_torch_dataloader = torch.utils.data.DataLoader(
                torch.utils.data.TensorDataset(
                    torch.tensor([0, 1]),
                    torch.tensor([0, 1])
                )
            )
            """
            )
        ],
        args_map={"data_torch_dataloader": "data_torch_dataloader"}
    )
)

TData = Union(str, Sequence, Iterable, 'pandas.DataFrame')
TLabels = Union(int, Sequence, Iterable, 'pandas.DataFrame')

PData = Parameter("data", typ=TData, desc="A data source.")
PLabels = Parameter("label", typ=TLabels, desc="A labels source.")

PFieldText = Parameter(
    "field_text",
    str,
    "Name of the text field in a data source.",
    help_info=HelpInfo(
        definition=[
            "# field_text represents the name of the text field in data_pandas",
            "field_text = 'text' # TODO: Replace me"
        ],
        args_map={"field_text": "field_text"}
    )
)
PFieldLabel = Parameter(
    "field_label",
    str,
    "Name of the label field in a data source.",
    help_info=HelpInfo(
        definition=[
            "# field_label represents the name of the label field in data_pandas",
            "field_label = 'label' # TODO: Replace me"
        ],
        args_map={"field_label": "field_label"}
    )
)
PFieldsMeta = Parameter(
    "fields_meta",
    typ=Sequence[str],
    desc="Metadata fields.",
    help_info=HelpInfo(
        definition=[
            "# fields_meta represents the names of metadata fields in data_pandas",
            "fields_meta = ['meta1', 'meta2'] # TODO: Replace me"
        ],
        args_map={"fields_meta": "fields_meta"}
    )
)


# Here only for its signature:
def example_ds_from_source(data_path: Path) -> Iterable[Any]:
    ...


PDSFromSource = Parameter(
    "ds_from_source",
    desc="Loads a dataset given a path",
    typ=Function(inspect.signature(example_ds_from_source)),
    help_info=HelpInfo(
        imports=["pathlib.Path"],
        definition=[
            inspect.cleandoc(
                """
            # Example using pandas to load a csv file as a dataframe
            def ds_from_source(data_path: Path) -> Iterable[Any]:
                # TODO: Replace me  
                return pd.read_csv(data_path)
            """
            )
        ],
        args_map={"ds_from_source": "ds_from_source"}
    )
)


# Here only for its signature:
def example_standardize_databatch(databatch: Any) -> Dict[str, Any]:
    ...


PStandardizeDatabatch = Parameter(
    "standardize_databatch",
    desc=
    "Function converting a batch of data to a dictionary with keys 'ids', 'text', and 'labels'.",
    typ=Function(inspect.signature(example_standardize_databatch)),
    help_info=HelpInfo(
        imports=["typing.Dict", "typing.Any"],
        definition=[
            inspect.cleandoc(
                """
            def standardize_databatch(databatch: Any) -> Dict[str, Any]:
                # TODO: Implement get_ids_from_databatch, get_text_from_databatch, get_labels_from_databatch
                return {
                    "ids": get_ids_from_databatch(databatch),
                    "text": get_text_from_databatch(databatch),
                    "labels": get_labels_from_databatch(databatch),
                }
            """
            ),
        ],
        args_map={"standardize_databatch": "standardize_databatch"}
    )
)

PTokenEmbeddingsLayer = Parameter(
    "token_embeddings_layer",
    desc=(
        "The model layer where token embeddings are computed. "
        "See Also `PTokenEmbeddingsAnchor`."
    ),
    typ=str,
    help_info=HelpInfo(
        definition=[
            "# token_embeddings_layer represents the name of the layer where token embeddings are computed",
            "token_embeddings_layer = 'embedding' # TODO: Replace me"
        ],
        args_map={"token_embeddings_layer": "token_embeddings_layer"}
    )
)

PTokenEmbeddingsAnchor = Parameter(
    "token_embeddings_anchor",
    desc=
    "The side of token_embeddings_layer where token embeddings are computed. Must be either 'out' or 'in'.",
    typ=LayerAnchor,
    help_info=HelpInfo(
        definition=[
            "# token_embeddings_anchor represents the side of token_embeddings_layer where token embeddings are computed",
            "token_embeddings_anchor = 'out' # TODO: Replace me"
        ],
        args_map={"token_embeddings_anchor": "token_embeddings_anchor"}
    )
)

POutputLayer = Parameter(
    "output_layer",
    desc=(
        "The model layer from which a quantity of interest is defined. ",
        "See also `POutputAnchor`."
    ),
    typ=str,
    help_info=HelpInfo(
        definition=[
            "# output_layer represents the name of the output layer of the model",
            "output_layer = 'output' # TODO: Replace me"
        ],
        args_map={"output_layer": "output_layer"}
    )
)

POutputAnchor = Parameter(
    "output_anchor",
    desc=
    "The side of output_layer where the output is calculated. Must be either 'out' or 'in'.",
    typ=LayerAnchor,
    help_info=HelpInfo(
        definition=[
            "# output_anchor represents the side of output_layer where the output tensor is calculated.",
            "output_anchor = 'out' # TODO: Replace me"
        ],
        args_map={"output_anchor": "output_anchor"}
    )
)

PNOutputNeurons = Parameter(
    "n_output_neurons",
    desc="Number of neurons in the output layer.",
    typ=int,
    help_info=HelpInfo(
        definition=[
            "# n_output_neurons represents the number of neurons in the output layer",
            "n_output_neurons = 2 # TODO: Replace me",
        ],
        args_map={"n_output_neurons": "n_output_neurons"}
    )
)

PNRecords = Parameter(
    "n_records",
    desc="INTERNAL USE ONLY: data length",
    typ=int,
    help_info=HelpInfo(
        definition=[
            "# n_records represents the number of records in the dataset",
            "n_records = 100 # TODO: Replace me"
        ],
        args_map={"n_records": "n_records"}
    )
)

PNMetricsRecords = Parameter(
    "n_metrics_records",
    desc="The number of records in the metrics dataset",
    typ=int,
    help_info=HelpInfo(
        definition=[
            "# n_metrics_records represents the number of records in the metrics dataset",
            "n_metrics_records = 100 # TODO: Replace me"
        ],
        args_map={"n_metrics_records": "n_metrics_records"}
    )
)

PRefToken = Parameter(
    "ref_token",
    desc=
    "A semantically 'neutral' token used for generating baselines for influences.",
    typ=str,
    help_info=HelpInfo(
        definition=[
            "# ref_token represents the token used for generating baselines for influences",
            "ref_token = '<PAD>' # TODO: Replace me"
        ],
        args_map={"ref_token": "ref_token"}
    )
)

PUseTrainingMode = Parameter(
    "use_training_mode",
    desc="Use training mode when computing gradients.",
    typ=bool,
    help_info=HelpInfo(
        definition=[
            "# use_training_mode represents whether to use training mode when computing gradients",
            "use_training_mode = True # TODO: Replace me"
        ],
        args_map={"use_training_mode": "use_training_mode"}
    )
)

PResolution = Parameter(
    "resolution",
    desc=(
        "Baseline-to-instance interpolation resolution. "
        "Higher produces more accurate influences, but takes longer to compute."
    ),
    typ=int,
    help_info=HelpInfo(
        definition=[
            "# resolution represents the baseline-to-instance interpolation resolution",
            "resolution = 20 # TODO: Replace me"
        ],
        args_map={"resolution": "resolution"}
    )
)

PRebatchSize = Parameter(
    "rebatch_size",
    desc=(
        "The number of instances to send to a model at once. "
        "May result in out-of-memory error if set too large."
    ),
    typ=int,
    help_info=HelpInfo(
        definition=["rebatch_size = 32 # TODO: Replace me"],
        args_map={"rebatch_size": "rebatch_size"}
    )
)

PScoreType = Parameter(
    "score_type",
    desc=
    "The score type for your model. Must be one of (`probits`, `logits`, `regression`, `classification`). Defaults to `probits`",
    help_info=
    "score_type = 'probits'\nExplainer().set_model(score_type=score_type)",
    typ=str
)

PClassificationThreshold = Parameter(
    "classification_threshold",
    desc=
    "Threshold for binary classifiers. Must be between [0, 1]. Defaults to .5",
    help_info=
    "classification_threshold = .5\nExplainer().set_model(classification_threshold=classification_threshold)",
    typ=float
)

PTrulensWrapper = Parameter(
    "trulens_wrapper", desc="TruLens Model Wrapper", typ=ModelWrapper
)

# Parameters used in debugging/demos.
PDebugModel = Parameter(
    "debug_model",
    desc="",
    typ=str,
    help_info=HelpInfo(
        definition=["debug_model = 0 # NOTE: this is a debug argument"],
        args_map={"debug_model": "debug_model"}
    )
)
PDebugArg = Parameter(
    "debug_arg",
    desc="",
    typ=int,
    help_info=HelpInfo(
        definition=["debug_arg = 0 # NOTE: this is a debug argument"],
        args_map={"debug_arg": "debug_arg"}
    )
)
PDebugInfer = Parameter(
    "debug_infer",
    desc="",
    typ=int,
    help_info=HelpInfo(
        definition=["debug_infer = 0 # NOTE: this is a debug argument"],
        args_map={"debug_infer": "debug_infer"}
    )
)

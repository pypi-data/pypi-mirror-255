# autoredteam

Automated Red Teaming Test suite by [vijil](https://www.vijil.ai/).

## CLI calling patterns

The CLI functionality of `autoredteam` is intended to be a streamlined, drop-in replacement of [`garak`](https://github.com/leondz/garak/).
Currently, you can use it to kick off tests by either module (`--tests`) or dimension (`--dimensions`).

```
python -m autoredteam --model_type <> --model_name <> --tests <>
python -m autoredteam --model_type <> --model_name <> --dimensions <>
```
We currently support LLMs hosted on a number of model providers as agents. For a model provider, there are three possible deployment types: local model, public API, and private endpoint. Some providers offer only a subset of these deployment types.

The following table provides respective `--model_type` values for each such provider x deployment type. If a deployment type is not listed for a provider, the respective radio button should be inactive in the GUI.

| Agent | Deployment Type | `model_type`
|---|---|---|
| Anyscale | public API | `anyscale` |
| Hugging Face | local model | `huggingface` |
| | public API | `huggingface.InferenceAPI` |
| | private endpoint | `huggingface.InferenceEndpoint` |
| Mistral | public API | `mistral` |
| Replicate | public API | `replicate` |
| | private endpoint | `replicate.ReplicateEndpoint` |
| OctoAI | public API | `octo` |
| | private endpoint | `octo.OctoEndpoint` |
| OpenAI | public API | `openai` |
| Together | public API | `together` |

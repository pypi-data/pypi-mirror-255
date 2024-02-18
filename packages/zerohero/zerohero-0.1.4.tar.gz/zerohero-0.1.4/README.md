# Zero Hero: A Simple Zero-Shot Classifier

Zero Hero is a simple zero-shot classifier that is easy to use and works well for a variety of tasks. It is especially useful for classifying text that is unlabeled, and can even be applied to pseudo-label data.

### What is a zero-shot classifier?

A zero-shot text classifier is a machine learning model capable of classifying new data into categories or classes not seen during model training. Because these pre-trained models have been trained on such a large corpus of text, the model is able to infer the meaning of novel words and phrases and apply this knowledge to classify new text.

### Why use Zero Hero?

There are several reasons why you’d want to use Zero Hero:
 - It’s easy to use. You only need to create a list of the categories you want to classify text for, and then pass this list to the classifier.
 - It’s accurate. Zero Hero has been shown to be accurate on a variety of tasks.
 - It’s fast. Zero Hero is very efficient and can classify text quickly.

### Installation

To use Zero Hero, you first need to install the package using pip:
```
pip install zerohero
```

### How to use Zero Hero with SentenceTransformers (Easy)


To use SentenceTransformers, `model_type` must be passed as "sentence-transformers" and `model_name` supports any of [these](https://www.sbert.net/docs/pretrained_models.html) models.  

For examples:  


```python
from zerohero import make_zero_shot_classifier

# Create a classifier and pass the categories you wish to classify
categories = ['sports', 'politics', 'business', 'entertainment', 'science']
classifier = make_zero_shot_classifier(
    categories=categories,
    model_type="sentence-transformers",
    model_name="paraphrase-albert-small-v2",
)
```
Note that the categories passed to the classifier need to be semantically meaningful, i.e. categories of 1,2,3,4 would not be appropriate. Once you have created a classifier, you can use it to classify text using the following code:

```python
# Classify a piece of text
text = 'The president gave a speech today about the economy.'
result = classifier(text)

# Print the category
result["category"]
```
This will print the following output:
```
business
```
This output indicates the classifier is most confident that the text pertains to business.

### Using Zero Hero with OpenAI embedding models

In order to use and OpenAI model, you'll need an OpenAI API key.

Pass `model_type` as "open_ai" and `openai_api_key` as your OpenAI API key.

`model_name` can be any of:

```
"text-embedding-3-small",
"text-embedding-3-large",
"text-embedding-ada-002"
```

and should support other OpenAI embedding models as they are released.  

[Here](https://platform.openai.com/docs/guides/embeddings/embedding-models) is a list of current embedding models as OpenAI releases them. 

Here is an example:


```python

openai_api_key = "sk-..."

categories = ["cat", "dog", "mouse", "human"]
        zsc = make_zero_shot_classifier(
            categories=categories,
            model_type="openai",
            model_name=model_name,
            openai_api_key=openai_api_key,
        )
        result = zsc(cat_text)
        print(result)
```


### Why use Zero Hero instead of a prompt-based classifier?

There are several reasons why you might want to use Zero Hero instead of a prompt-based classifier:
 - Zero Hero is cheaper. A prompt-based classifier can be very expensive to use, especially if you have a lot of text to classify.
 - Zero Hero is more accurate. Prompt-based classifiers can be less accurate than zero-shot classifiers, especially on tasks that require a deep understanding of the text.
 - Zero Hero is easier to use. Prompt-based classifiers can be more difficult to use than zero-shot classifiers, especially if you are not familiar with machine learning.

The zero-shot classifier offers a cost-effective and efficient alternative to prompt-based classifiers for text categorization tasks. It can effectively classify text into predefined categories without the need for extensive training data by employing text embeddings and cosine similarity.. 
 - Text embeddings are created via the embedding function, which is used to convert text into a vector of numbers. This vector of numbers represents the meaning of the text. The zero-shot classifier uses the embedding function to compare the meaning of the text to the meaning of the categories.
 - Cosine similarity is a measure of similarity between two vectors. The zero-shot classifier uses cosine similarity to compare the meaning of the text to the meaning of the categories.

This approach significantly reduces architectural overhead compared to prompt-based classifiers that rely on generative models, resulting in a more scalable and resource-efficient solution. For instance, using an embedding/transformer model instead of a generative model can reduce the cost by a factor of ten. Additionally, the zero-shot classifier's ability to utilize pre-computed categories further enhances its performance and efficiency.

### Conclusion

Zero Hero is a simple and powerful zero-shot classifier that is easy to use and works well for a variety of tasks. It is a good choice for anyone who needs to classify text that is unlabeled or that has little data.

## Development Instructions

Install Dependencies: `poetry install --with dev`  
Configure pre-commit hooks: `poetry run pre-commit install`  
Manually run black: `poetry run black zerohero/* tests/*`  
Manually run pylint: `poetry run pylint zerohero/* tests/*`

import setuptools

#with open('requirements.txt') as f:
#    required = f.read().splitlines()
    
setuptools.setup(
    name = "apikeylogger",
    version = "1.0.0",
    author = "Federico Romeo",
    author_email = "federico.romeo.98@gmail.com",
    description = "This library allows you to log the OpenAI api usage by key without having to change your code",
    long_description = "todo",
    long_description_content_type = "text/markdown",
    url = "https://github.com/federicoromeo/apikeylogger",
    keywords  =  ['openai', 'apikey', 'logging'],
    project_urls = {
        'Source': 'https://github.com/federicoromeo/apikeylogger',  
    },
    packages = setuptools.find_packages(),
    include_package_data = True,
    classifiers = [],
    python_requires = ">=3.6",
    #install_requires = required,
    install_requires = [
        "openai >= 1.6.0",
        "python-dotenv >= 0.18.0",
        "tiktoken"
    ],
)

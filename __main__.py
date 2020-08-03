from data.apple.preprocess import main as preprocess_apple
from data.facebook.preprocess import main as preprocess_facebook
from data.google.preprocess import main as preprocess_google

if __name__ == '__main__':
    preprocess_apple()
    preprocess_facebook()
    preprocess_google()

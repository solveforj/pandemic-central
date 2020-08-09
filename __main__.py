#from data.apple.preprocess import main as preprocess_apple
#from data.facebook.preprocess import main as preprocess_facebook
#from data.google.preprocess import main as preprocess_google
import sys
print(sys.path[0])
sys.path.append(sys.path[0] + "/apple")
from data.merge import update

##if __name__ == '__main__':
#    preprocess_apple()#
#    preprocess_facebook()
#    preprocess_google()

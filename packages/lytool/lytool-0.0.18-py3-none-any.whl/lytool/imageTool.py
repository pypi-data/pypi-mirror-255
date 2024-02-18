import base64
from hashlib import md5

class ImageTool:
    def toB64(self, imagePath):
        '''
        功能：图片转base64
        imagePath: 图片地址
        return: base64编码
        '''
        with open(imagePath, "rb") as f:
            b64Str = bytes.decode(base64.b64encode(f.read()))
        return b64Str


    def toImage(self, base64str, absFilePath):
        '''
        功能：base64转图片
        base64str: string '/sdfasdf/asdfasf=='
        absFilePath: string '/var/www/html/images/imageName.png'
        '''
        b64 = base64.b64decode(base64str)
        with open(absFilePath, 'wb') as f:
            f.write(b64)

    def toMd5(self, data):
        '''
        功能: b64转md5
        '''

        return md5(data.encode('utf8')).hexdigest()

if __name__ == '__main__':
    itl = ImageTool()

    fileName = "添加好友.png"
    suffix = fileName.split('.')[-1]
    b64Str = itl.toB64(f"./{fileName}")
    NewFilename = itl.toMd5(b64Str) + f'.png'
    itl.toImage(b64Str, NewFilename)
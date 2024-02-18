# Generated from ../flash_patcher/antlr_source/PatchfileParser.g4 by ANTLR 4.13.1
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,24,137,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,7,12,2,13,7,13,
        2,14,7,14,1,0,1,0,1,0,1,0,1,1,4,1,36,8,1,11,1,12,1,37,1,1,1,1,1,
        1,1,1,1,2,4,2,45,8,2,11,2,12,2,46,1,3,1,3,1,3,1,3,1,3,1,3,1,4,1,
        4,1,4,1,4,1,5,4,5,60,8,5,11,5,12,5,61,1,5,1,5,1,5,1,5,1,5,1,5,1,
        5,1,6,1,6,1,6,1,7,4,7,75,8,7,11,7,12,7,76,1,7,1,7,1,7,1,7,1,7,1,
        7,1,7,1,8,4,8,87,8,8,11,8,12,8,88,1,9,1,9,1,9,1,9,1,10,1,10,1,10,
        1,11,1,11,1,11,1,12,1,12,1,12,1,12,1,12,1,12,1,12,5,12,108,8,12,
        10,12,12,12,111,9,12,1,13,3,13,114,8,13,1,13,1,13,1,13,3,13,119,
        8,13,1,13,3,13,122,8,13,1,13,1,13,1,13,1,13,1,13,3,13,129,8,13,1,
        13,1,13,3,13,133,8,13,1,14,1,14,1,14,0,0,15,0,2,4,6,8,10,12,14,16,
        18,20,22,24,26,28,0,0,140,0,30,1,0,0,0,2,35,1,0,0,0,4,44,1,0,0,0,
        6,48,1,0,0,0,8,54,1,0,0,0,10,59,1,0,0,0,12,70,1,0,0,0,14,74,1,0,
        0,0,16,86,1,0,0,0,18,90,1,0,0,0,20,94,1,0,0,0,22,97,1,0,0,0,24,109,
        1,0,0,0,26,132,1,0,0,0,28,134,1,0,0,0,30,31,5,1,0,0,31,32,5,8,0,
        0,32,33,3,26,13,0,33,1,1,0,0,0,34,36,3,0,0,0,35,34,1,0,0,0,36,37,
        1,0,0,0,37,35,1,0,0,0,37,38,1,0,0,0,38,39,1,0,0,0,39,40,5,9,0,0,
        40,41,3,4,2,0,41,42,5,21,0,0,42,3,1,0,0,0,43,45,5,22,0,0,44,43,1,
        0,0,0,45,46,1,0,0,0,46,44,1,0,0,0,46,47,1,0,0,0,47,5,1,0,0,0,48,
        49,5,3,0,0,49,50,5,8,0,0,50,51,3,26,13,0,51,52,5,16,0,0,52,53,3,
        26,13,0,53,7,1,0,0,0,54,55,5,4,0,0,55,56,5,8,0,0,56,57,3,26,13,0,
        57,9,1,0,0,0,58,60,3,8,4,0,59,58,1,0,0,0,60,61,1,0,0,0,61,59,1,0,
        0,0,61,62,1,0,0,0,62,63,1,0,0,0,63,64,5,10,0,0,64,65,3,16,8,0,65,
        66,5,23,0,0,66,67,5,9,0,0,67,68,3,4,2,0,68,69,5,21,0,0,69,11,1,0,
        0,0,70,71,5,5,0,0,71,72,5,8,0,0,72,13,1,0,0,0,73,75,3,12,6,0,74,
        73,1,0,0,0,75,76,1,0,0,0,76,74,1,0,0,0,76,77,1,0,0,0,77,78,1,0,0,
        0,78,79,5,10,0,0,79,80,3,16,8,0,80,81,5,23,0,0,81,82,5,9,0,0,82,
        83,3,4,2,0,83,84,5,21,0,0,84,15,1,0,0,0,85,87,5,24,0,0,86,85,1,0,
        0,0,87,88,1,0,0,0,88,86,1,0,0,0,88,89,1,0,0,0,89,17,1,0,0,0,90,91,
        5,2,0,0,91,92,3,28,14,0,92,93,3,28,14,0,93,19,1,0,0,0,94,95,5,6,
        0,0,95,96,3,28,14,0,96,21,1,0,0,0,97,98,5,7,0,0,98,99,3,28,14,0,
        99,23,1,0,0,0,100,108,3,2,1,0,101,108,3,6,3,0,102,108,3,10,5,0,103,
        108,3,14,7,0,104,108,3,18,9,0,105,108,3,20,10,0,106,108,3,22,11,
        0,107,100,1,0,0,0,107,101,1,0,0,0,107,102,1,0,0,0,107,103,1,0,0,
        0,107,104,1,0,0,0,107,105,1,0,0,0,107,106,1,0,0,0,108,111,1,0,0,
        0,109,107,1,0,0,0,109,110,1,0,0,0,110,25,1,0,0,0,111,109,1,0,0,0,
        112,114,5,13,0,0,113,112,1,0,0,0,113,114,1,0,0,0,114,115,1,0,0,0,
        115,116,5,11,0,0,116,118,5,18,0,0,117,119,5,15,0,0,118,117,1,0,0,
        0,118,119,1,0,0,0,119,121,1,0,0,0,120,122,5,14,0,0,121,120,1,0,0,
        0,121,122,1,0,0,0,122,133,1,0,0,0,123,124,5,10,0,0,124,125,3,16,
        8,0,125,128,5,23,0,0,126,127,5,17,0,0,127,129,5,15,0,0,128,126,1,
        0,0,0,128,129,1,0,0,0,129,133,1,0,0,0,130,133,5,15,0,0,131,133,5,
        12,0,0,132,113,1,0,0,0,132,123,1,0,0,0,132,130,1,0,0,0,132,131,1,
        0,0,0,133,27,1,0,0,0,134,135,5,18,0,0,135,29,1,0,0,0,12,37,46,61,
        76,88,107,109,113,118,121,128,132
    ]

class PatchfileParser ( Parser ):

    grammarFileName = "PatchfileParser.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "'('", "')'", "<INVALID>", "'-'", "'+'" ]

    symbolicNames = [ "<INVALID>", "ADD", "ADD_ASSET", "REMOVE", "REPLACE", 
                      "REPLACE_ALL", "EXEC_PATCHER", "EXEC_PYTHON", "FILENAME", 
                      "BEGIN_PATCH", "BEGIN_CONTENT", "FUNCTION", "END", 
                      "OPEN_BLOCK", "CLOSE_BLOCK", "INTEGER", "DASH", "PLUS", 
                      "TEXT_BLOCK", "WHITESPACE", "COMMENT", "END_PATCH", 
                      "AS_TEXT", "END_CONTENT", "CONTENT_TEXT" ]

    RULE_addBlockHeader = 0
    RULE_addBlock = 1
    RULE_addBlockText = 2
    RULE_removeBlock = 3
    RULE_replaceNthBlockHeader = 4
    RULE_replaceNthBlock = 5
    RULE_replaceAllBlockHeader = 6
    RULE_replaceAllBlock = 7
    RULE_replaceBlockText = 8
    RULE_addAssetBlock = 9
    RULE_execPatcherBlock = 10
    RULE_execPythonBlock = 11
    RULE_root = 12
    RULE_locationToken = 13
    RULE_file_name = 14

    ruleNames =  [ "addBlockHeader", "addBlock", "addBlockText", "removeBlock", 
                   "replaceNthBlockHeader", "replaceNthBlock", "replaceAllBlockHeader", 
                   "replaceAllBlock", "replaceBlockText", "addAssetBlock", 
                   "execPatcherBlock", "execPythonBlock", "root", "locationToken", 
                   "file_name" ]

    EOF = Token.EOF
    ADD=1
    ADD_ASSET=2
    REMOVE=3
    REPLACE=4
    REPLACE_ALL=5
    EXEC_PATCHER=6
    EXEC_PYTHON=7
    FILENAME=8
    BEGIN_PATCH=9
    BEGIN_CONTENT=10
    FUNCTION=11
    END=12
    OPEN_BLOCK=13
    CLOSE_BLOCK=14
    INTEGER=15
    DASH=16
    PLUS=17
    TEXT_BLOCK=18
    WHITESPACE=19
    COMMENT=20
    END_PATCH=21
    AS_TEXT=22
    END_CONTENT=23
    CONTENT_TEXT=24

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.1")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class AddBlockHeaderContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ADD(self):
            return self.getToken(PatchfileParser.ADD, 0)

        def FILENAME(self):
            return self.getToken(PatchfileParser.FILENAME, 0)

        def locationToken(self):
            return self.getTypedRuleContext(PatchfileParser.LocationTokenContext,0)


        def getRuleIndex(self):
            return PatchfileParser.RULE_addBlockHeader

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAddBlockHeader" ):
                listener.enterAddBlockHeader(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAddBlockHeader" ):
                listener.exitAddBlockHeader(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAddBlockHeader" ):
                return visitor.visitAddBlockHeader(self)
            else:
                return visitor.visitChildren(self)




    def addBlockHeader(self):

        localctx = PatchfileParser.AddBlockHeaderContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_addBlockHeader)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 30
            self.match(PatchfileParser.ADD)
            self.state = 31
            self.match(PatchfileParser.FILENAME)
            self.state = 32
            self.locationToken()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AddBlockContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def BEGIN_PATCH(self):
            return self.getToken(PatchfileParser.BEGIN_PATCH, 0)

        def addBlockText(self):
            return self.getTypedRuleContext(PatchfileParser.AddBlockTextContext,0)


        def END_PATCH(self):
            return self.getToken(PatchfileParser.END_PATCH, 0)

        def addBlockHeader(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PatchfileParser.AddBlockHeaderContext)
            else:
                return self.getTypedRuleContext(PatchfileParser.AddBlockHeaderContext,i)


        def getRuleIndex(self):
            return PatchfileParser.RULE_addBlock

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAddBlock" ):
                listener.enterAddBlock(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAddBlock" ):
                listener.exitAddBlock(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAddBlock" ):
                return visitor.visitAddBlock(self)
            else:
                return visitor.visitChildren(self)




    def addBlock(self):

        localctx = PatchfileParser.AddBlockContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_addBlock)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 35 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 34
                self.addBlockHeader()
                self.state = 37 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==1):
                    break

            self.state = 39
            self.match(PatchfileParser.BEGIN_PATCH)
            self.state = 40
            self.addBlockText()
            self.state = 41
            self.match(PatchfileParser.END_PATCH)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AddBlockTextContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def AS_TEXT(self, i:int=None):
            if i is None:
                return self.getTokens(PatchfileParser.AS_TEXT)
            else:
                return self.getToken(PatchfileParser.AS_TEXT, i)

        def getRuleIndex(self):
            return PatchfileParser.RULE_addBlockText

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAddBlockText" ):
                listener.enterAddBlockText(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAddBlockText" ):
                listener.exitAddBlockText(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAddBlockText" ):
                return visitor.visitAddBlockText(self)
            else:
                return visitor.visitChildren(self)




    def addBlockText(self):

        localctx = PatchfileParser.AddBlockTextContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_addBlockText)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 44 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 43
                self.match(PatchfileParser.AS_TEXT)
                self.state = 46 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==22):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class RemoveBlockContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def REMOVE(self):
            return self.getToken(PatchfileParser.REMOVE, 0)

        def FILENAME(self):
            return self.getToken(PatchfileParser.FILENAME, 0)

        def locationToken(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PatchfileParser.LocationTokenContext)
            else:
                return self.getTypedRuleContext(PatchfileParser.LocationTokenContext,i)


        def DASH(self):
            return self.getToken(PatchfileParser.DASH, 0)

        def getRuleIndex(self):
            return PatchfileParser.RULE_removeBlock

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterRemoveBlock" ):
                listener.enterRemoveBlock(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitRemoveBlock" ):
                listener.exitRemoveBlock(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitRemoveBlock" ):
                return visitor.visitRemoveBlock(self)
            else:
                return visitor.visitChildren(self)




    def removeBlock(self):

        localctx = PatchfileParser.RemoveBlockContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_removeBlock)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 48
            self.match(PatchfileParser.REMOVE)
            self.state = 49
            self.match(PatchfileParser.FILENAME)
            self.state = 50
            self.locationToken()
            self.state = 51
            self.match(PatchfileParser.DASH)
            self.state = 52
            self.locationToken()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ReplaceNthBlockHeaderContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def REPLACE(self):
            return self.getToken(PatchfileParser.REPLACE, 0)

        def FILENAME(self):
            return self.getToken(PatchfileParser.FILENAME, 0)

        def locationToken(self):
            return self.getTypedRuleContext(PatchfileParser.LocationTokenContext,0)


        def getRuleIndex(self):
            return PatchfileParser.RULE_replaceNthBlockHeader

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterReplaceNthBlockHeader" ):
                listener.enterReplaceNthBlockHeader(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitReplaceNthBlockHeader" ):
                listener.exitReplaceNthBlockHeader(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitReplaceNthBlockHeader" ):
                return visitor.visitReplaceNthBlockHeader(self)
            else:
                return visitor.visitChildren(self)




    def replaceNthBlockHeader(self):

        localctx = PatchfileParser.ReplaceNthBlockHeaderContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_replaceNthBlockHeader)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 54
            self.match(PatchfileParser.REPLACE)
            self.state = 55
            self.match(PatchfileParser.FILENAME)
            self.state = 56
            self.locationToken()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ReplaceNthBlockContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def BEGIN_CONTENT(self):
            return self.getToken(PatchfileParser.BEGIN_CONTENT, 0)

        def replaceBlockText(self):
            return self.getTypedRuleContext(PatchfileParser.ReplaceBlockTextContext,0)


        def END_CONTENT(self):
            return self.getToken(PatchfileParser.END_CONTENT, 0)

        def BEGIN_PATCH(self):
            return self.getToken(PatchfileParser.BEGIN_PATCH, 0)

        def addBlockText(self):
            return self.getTypedRuleContext(PatchfileParser.AddBlockTextContext,0)


        def END_PATCH(self):
            return self.getToken(PatchfileParser.END_PATCH, 0)

        def replaceNthBlockHeader(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PatchfileParser.ReplaceNthBlockHeaderContext)
            else:
                return self.getTypedRuleContext(PatchfileParser.ReplaceNthBlockHeaderContext,i)


        def getRuleIndex(self):
            return PatchfileParser.RULE_replaceNthBlock

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterReplaceNthBlock" ):
                listener.enterReplaceNthBlock(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitReplaceNthBlock" ):
                listener.exitReplaceNthBlock(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitReplaceNthBlock" ):
                return visitor.visitReplaceNthBlock(self)
            else:
                return visitor.visitChildren(self)




    def replaceNthBlock(self):

        localctx = PatchfileParser.ReplaceNthBlockContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_replaceNthBlock)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 59 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 58
                self.replaceNthBlockHeader()
                self.state = 61 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==4):
                    break

            self.state = 63
            self.match(PatchfileParser.BEGIN_CONTENT)
            self.state = 64
            self.replaceBlockText()
            self.state = 65
            self.match(PatchfileParser.END_CONTENT)
            self.state = 66
            self.match(PatchfileParser.BEGIN_PATCH)
            self.state = 67
            self.addBlockText()
            self.state = 68
            self.match(PatchfileParser.END_PATCH)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ReplaceAllBlockHeaderContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def REPLACE_ALL(self):
            return self.getToken(PatchfileParser.REPLACE_ALL, 0)

        def FILENAME(self):
            return self.getToken(PatchfileParser.FILENAME, 0)

        def getRuleIndex(self):
            return PatchfileParser.RULE_replaceAllBlockHeader

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterReplaceAllBlockHeader" ):
                listener.enterReplaceAllBlockHeader(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitReplaceAllBlockHeader" ):
                listener.exitReplaceAllBlockHeader(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitReplaceAllBlockHeader" ):
                return visitor.visitReplaceAllBlockHeader(self)
            else:
                return visitor.visitChildren(self)




    def replaceAllBlockHeader(self):

        localctx = PatchfileParser.ReplaceAllBlockHeaderContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_replaceAllBlockHeader)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 70
            self.match(PatchfileParser.REPLACE_ALL)
            self.state = 71
            self.match(PatchfileParser.FILENAME)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ReplaceAllBlockContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def BEGIN_CONTENT(self):
            return self.getToken(PatchfileParser.BEGIN_CONTENT, 0)

        def replaceBlockText(self):
            return self.getTypedRuleContext(PatchfileParser.ReplaceBlockTextContext,0)


        def END_CONTENT(self):
            return self.getToken(PatchfileParser.END_CONTENT, 0)

        def BEGIN_PATCH(self):
            return self.getToken(PatchfileParser.BEGIN_PATCH, 0)

        def addBlockText(self):
            return self.getTypedRuleContext(PatchfileParser.AddBlockTextContext,0)


        def END_PATCH(self):
            return self.getToken(PatchfileParser.END_PATCH, 0)

        def replaceAllBlockHeader(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PatchfileParser.ReplaceAllBlockHeaderContext)
            else:
                return self.getTypedRuleContext(PatchfileParser.ReplaceAllBlockHeaderContext,i)


        def getRuleIndex(self):
            return PatchfileParser.RULE_replaceAllBlock

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterReplaceAllBlock" ):
                listener.enterReplaceAllBlock(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitReplaceAllBlock" ):
                listener.exitReplaceAllBlock(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitReplaceAllBlock" ):
                return visitor.visitReplaceAllBlock(self)
            else:
                return visitor.visitChildren(self)




    def replaceAllBlock(self):

        localctx = PatchfileParser.ReplaceAllBlockContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_replaceAllBlock)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 74 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 73
                self.replaceAllBlockHeader()
                self.state = 76 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==5):
                    break

            self.state = 78
            self.match(PatchfileParser.BEGIN_CONTENT)
            self.state = 79
            self.replaceBlockText()
            self.state = 80
            self.match(PatchfileParser.END_CONTENT)
            self.state = 81
            self.match(PatchfileParser.BEGIN_PATCH)
            self.state = 82
            self.addBlockText()
            self.state = 83
            self.match(PatchfileParser.END_PATCH)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ReplaceBlockTextContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def CONTENT_TEXT(self, i:int=None):
            if i is None:
                return self.getTokens(PatchfileParser.CONTENT_TEXT)
            else:
                return self.getToken(PatchfileParser.CONTENT_TEXT, i)

        def getRuleIndex(self):
            return PatchfileParser.RULE_replaceBlockText

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterReplaceBlockText" ):
                listener.enterReplaceBlockText(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitReplaceBlockText" ):
                listener.exitReplaceBlockText(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitReplaceBlockText" ):
                return visitor.visitReplaceBlockText(self)
            else:
                return visitor.visitChildren(self)




    def replaceBlockText(self):

        localctx = PatchfileParser.ReplaceBlockTextContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_replaceBlockText)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 86 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 85
                self.match(PatchfileParser.CONTENT_TEXT)
                self.state = 88 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==24):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AddAssetBlockContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser
            self.local = None # File_nameContext
            self.swf = None # File_nameContext

        def ADD_ASSET(self):
            return self.getToken(PatchfileParser.ADD_ASSET, 0)

        def file_name(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PatchfileParser.File_nameContext)
            else:
                return self.getTypedRuleContext(PatchfileParser.File_nameContext,i)


        def getRuleIndex(self):
            return PatchfileParser.RULE_addAssetBlock

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAddAssetBlock" ):
                listener.enterAddAssetBlock(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAddAssetBlock" ):
                listener.exitAddAssetBlock(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAddAssetBlock" ):
                return visitor.visitAddAssetBlock(self)
            else:
                return visitor.visitChildren(self)




    def addAssetBlock(self):

        localctx = PatchfileParser.AddAssetBlockContext(self, self._ctx, self.state)
        self.enterRule(localctx, 18, self.RULE_addAssetBlock)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 90
            self.match(PatchfileParser.ADD_ASSET)
            self.state = 91
            localctx.local = self.file_name()
            self.state = 92
            localctx.swf = self.file_name()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ExecPatcherBlockContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EXEC_PATCHER(self):
            return self.getToken(PatchfileParser.EXEC_PATCHER, 0)

        def file_name(self):
            return self.getTypedRuleContext(PatchfileParser.File_nameContext,0)


        def getRuleIndex(self):
            return PatchfileParser.RULE_execPatcherBlock

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterExecPatcherBlock" ):
                listener.enterExecPatcherBlock(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitExecPatcherBlock" ):
                listener.exitExecPatcherBlock(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitExecPatcherBlock" ):
                return visitor.visitExecPatcherBlock(self)
            else:
                return visitor.visitChildren(self)




    def execPatcherBlock(self):

        localctx = PatchfileParser.ExecPatcherBlockContext(self, self._ctx, self.state)
        self.enterRule(localctx, 20, self.RULE_execPatcherBlock)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 94
            self.match(PatchfileParser.EXEC_PATCHER)
            self.state = 95
            self.file_name()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ExecPythonBlockContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EXEC_PYTHON(self):
            return self.getToken(PatchfileParser.EXEC_PYTHON, 0)

        def file_name(self):
            return self.getTypedRuleContext(PatchfileParser.File_nameContext,0)


        def getRuleIndex(self):
            return PatchfileParser.RULE_execPythonBlock

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterExecPythonBlock" ):
                listener.enterExecPythonBlock(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitExecPythonBlock" ):
                listener.exitExecPythonBlock(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitExecPythonBlock" ):
                return visitor.visitExecPythonBlock(self)
            else:
                return visitor.visitChildren(self)




    def execPythonBlock(self):

        localctx = PatchfileParser.ExecPythonBlockContext(self, self._ctx, self.state)
        self.enterRule(localctx, 22, self.RULE_execPythonBlock)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 97
            self.match(PatchfileParser.EXEC_PYTHON)
            self.state = 98
            self.file_name()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class RootContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def addBlock(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PatchfileParser.AddBlockContext)
            else:
                return self.getTypedRuleContext(PatchfileParser.AddBlockContext,i)


        def removeBlock(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PatchfileParser.RemoveBlockContext)
            else:
                return self.getTypedRuleContext(PatchfileParser.RemoveBlockContext,i)


        def replaceNthBlock(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PatchfileParser.ReplaceNthBlockContext)
            else:
                return self.getTypedRuleContext(PatchfileParser.ReplaceNthBlockContext,i)


        def replaceAllBlock(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PatchfileParser.ReplaceAllBlockContext)
            else:
                return self.getTypedRuleContext(PatchfileParser.ReplaceAllBlockContext,i)


        def addAssetBlock(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PatchfileParser.AddAssetBlockContext)
            else:
                return self.getTypedRuleContext(PatchfileParser.AddAssetBlockContext,i)


        def execPatcherBlock(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PatchfileParser.ExecPatcherBlockContext)
            else:
                return self.getTypedRuleContext(PatchfileParser.ExecPatcherBlockContext,i)


        def execPythonBlock(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PatchfileParser.ExecPythonBlockContext)
            else:
                return self.getTypedRuleContext(PatchfileParser.ExecPythonBlockContext,i)


        def getRuleIndex(self):
            return PatchfileParser.RULE_root

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterRoot" ):
                listener.enterRoot(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitRoot" ):
                listener.exitRoot(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitRoot" ):
                return visitor.visitRoot(self)
            else:
                return visitor.visitChildren(self)




    def root(self):

        localctx = PatchfileParser.RootContext(self, self._ctx, self.state)
        self.enterRule(localctx, 24, self.RULE_root)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 109
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 254) != 0):
                self.state = 107
                self._errHandler.sync(self)
                token = self._input.LA(1)
                if token in [1]:
                    self.state = 100
                    self.addBlock()
                    pass
                elif token in [3]:
                    self.state = 101
                    self.removeBlock()
                    pass
                elif token in [4]:
                    self.state = 102
                    self.replaceNthBlock()
                    pass
                elif token in [5]:
                    self.state = 103
                    self.replaceAllBlock()
                    pass
                elif token in [2]:
                    self.state = 104
                    self.addAssetBlock()
                    pass
                elif token in [6]:
                    self.state = 105
                    self.execPatcherBlock()
                    pass
                elif token in [7]:
                    self.state = 106
                    self.execPythonBlock()
                    pass
                else:
                    raise NoViableAltException(self)

                self.state = 111
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class LocationTokenContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return PatchfileParser.RULE_locationToken

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)



    class FunctionContext(LocationTokenContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a PatchfileParser.LocationTokenContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def FUNCTION(self):
            return self.getToken(PatchfileParser.FUNCTION, 0)
        def TEXT_BLOCK(self):
            return self.getToken(PatchfileParser.TEXT_BLOCK, 0)
        def OPEN_BLOCK(self):
            return self.getToken(PatchfileParser.OPEN_BLOCK, 0)
        def INTEGER(self):
            return self.getToken(PatchfileParser.INTEGER, 0)
        def CLOSE_BLOCK(self):
            return self.getToken(PatchfileParser.CLOSE_BLOCK, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterFunction" ):
                listener.enterFunction(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitFunction" ):
                listener.exitFunction(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitFunction" ):
                return visitor.visitFunction(self)
            else:
                return visitor.visitChildren(self)


    class EndContext(LocationTokenContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a PatchfileParser.LocationTokenContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def END(self):
            return self.getToken(PatchfileParser.END, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterEnd" ):
                listener.enterEnd(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitEnd" ):
                listener.exitEnd(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitEnd" ):
                return visitor.visitEnd(self)
            else:
                return visitor.visitChildren(self)


    class TextContext(LocationTokenContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a PatchfileParser.LocationTokenContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def BEGIN_CONTENT(self):
            return self.getToken(PatchfileParser.BEGIN_CONTENT, 0)
        def replaceBlockText(self):
            return self.getTypedRuleContext(PatchfileParser.ReplaceBlockTextContext,0)

        def END_CONTENT(self):
            return self.getToken(PatchfileParser.END_CONTENT, 0)
        def PLUS(self):
            return self.getToken(PatchfileParser.PLUS, 0)
        def INTEGER(self):
            return self.getToken(PatchfileParser.INTEGER, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterText" ):
                listener.enterText(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitText" ):
                listener.exitText(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitText" ):
                return visitor.visitText(self)
            else:
                return visitor.visitChildren(self)


    class LineNumberContext(LocationTokenContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a PatchfileParser.LocationTokenContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def INTEGER(self):
            return self.getToken(PatchfileParser.INTEGER, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLineNumber" ):
                listener.enterLineNumber(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLineNumber" ):
                listener.exitLineNumber(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLineNumber" ):
                return visitor.visitLineNumber(self)
            else:
                return visitor.visitChildren(self)



    def locationToken(self):

        localctx = PatchfileParser.LocationTokenContext(self, self._ctx, self.state)
        self.enterRule(localctx, 26, self.RULE_locationToken)
        self._la = 0 # Token type
        try:
            self.state = 132
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [11, 13]:
                localctx = PatchfileParser.FunctionContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 113
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==13:
                    self.state = 112
                    self.match(PatchfileParser.OPEN_BLOCK)


                self.state = 115
                self.match(PatchfileParser.FUNCTION)
                self.state = 116
                self.match(PatchfileParser.TEXT_BLOCK)
                self.state = 118
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==15:
                    self.state = 117
                    self.match(PatchfileParser.INTEGER)


                self.state = 121
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==14:
                    self.state = 120
                    self.match(PatchfileParser.CLOSE_BLOCK)


                pass
            elif token in [10]:
                localctx = PatchfileParser.TextContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 123
                self.match(PatchfileParser.BEGIN_CONTENT)
                self.state = 124
                self.replaceBlockText()
                self.state = 125
                self.match(PatchfileParser.END_CONTENT)
                self.state = 128
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==17:
                    self.state = 126
                    self.match(PatchfileParser.PLUS)
                    self.state = 127
                    self.match(PatchfileParser.INTEGER)


                pass
            elif token in [15]:
                localctx = PatchfileParser.LineNumberContext(self, localctx)
                self.enterOuterAlt(localctx, 3)
                self.state = 130
                self.match(PatchfileParser.INTEGER)
                pass
            elif token in [12]:
                localctx = PatchfileParser.EndContext(self, localctx)
                self.enterOuterAlt(localctx, 4)
                self.state = 131
                self.match(PatchfileParser.END)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class File_nameContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def TEXT_BLOCK(self):
            return self.getToken(PatchfileParser.TEXT_BLOCK, 0)

        def getRuleIndex(self):
            return PatchfileParser.RULE_file_name

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterFile_name" ):
                listener.enterFile_name(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitFile_name" ):
                listener.exitFile_name(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitFile_name" ):
                return visitor.visitFile_name(self)
            else:
                return visitor.visitChildren(self)




    def file_name(self):

        localctx = PatchfileParser.File_nameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 28, self.RULE_file_name)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 134
            self.match(PatchfileParser.TEXT_BLOCK)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx






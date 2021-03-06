# -*- coding: utf-8 -*-
import wx
import wx.xrc
from calculate import *
import threading
import time
from iohandle import *
import gettext
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
###########################################################################
# Class MyFrame1
###########################################################################


class MyFrame1 (wx.Frame):
    res = []
    creatvar = locals()
    eve = threading.Event()
    ratio = [0, 0]

    def __init__(self, parent):
        # 多语言
        gettext.install('lang', './locale/', unicode=False)
        choices = ['简体中文', '繁體中文', 'English']
        dialog = wx.SingleChoiceDialog(None, "语言选择", "请选择语言", choices)
        if dialog.ShowModal() == wx.ID_OK:
            langu = dialog.GetStringSelection()
            if langu == u'English':
                gettext.translation('lang', './locale/',
                                    languages=['en_US']).install(True)
            if langu == u'繁體中文':
                gettext.translation('lang', './locale/',
                                    languages=['zh_HK']).install(True)
        ####################################################################
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title=wx.EmptyString, pos=wx.DefaultPosition, size=wx.Size(
            600, 500), style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)

        gbSizer1 = wx.GridBagSizer(10, 10)
        gbSizer1.SetFlexibleDirection(wx.BOTH)
        gbSizer1.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        # 生成控件
        self.btnStart = wx.Button(self, wx.ID_ANY, _(u"开始答题"))
        gbSizer1.Add(self.btnStart, span=(1, 1), pos=(1, 6))

        self.labTime = wx.StaticText(self, wx.ID_ANY, _(u"时间:"))
        gbSizer1.Add(self.labTime, span=(1, 1), pos=(
            2, 0), flag=wx.EXPAND, border=3)

        self.labTime1 = wx.StaticText(self, wx.ID_ANY, u"0:0:0")
        gbSizer1.Add(self.labTime1, span=(1, 1),
                     pos=(2, 1), flag=wx.EXPAND, border=3)
        self.labRatio = wx.StaticText(self, wx.ID_ANY, u"")
        gbSizer1.Add(self.labRatio, span=(1, 1),
                     pos=(2, 3), flag=wx.EXPAND, border=3)
        for i in range(1, 6):
            self.creatvar['self.labQues' +
                          str(i)] = wx.StaticText(self, wx.ID_ANY, u"")
            gbSizer1.Add(self.creatvar['self.labQues' + str(i)], span=(1, 5),
                         pos=(i + 2, 0), flag=wx.ALIGN_CENTER_VERTICAL, border=3)
            self.creatvar['self.texAns' +
                          str(i)] = wx.TextCtrl(self, i - 1, wx.EmptyString)
            gbSizer1.Add(self.creatvar['self.texAns' + str(i)],
                         pos=(i + 2, 6), flag=wx.ALIGN_CENTER_VERTICAL)
            self.creatvar['self.texAns' + str(i)].Disable()
            self.creatvar['self.labCor' +
                          str(i)] = wx.StaticText(self, i + 4, u"")
            gbSizer1.Add(self.creatvar['self.labCor' + str(i)],
                         pos=(i + 2, 7), flag=wx.ALIGN_CENTER_VERTICAL)

        self.btnNext = wx.Button(self, wx.ID_ANY, _(u"再来五题"))
        gbSizer1.Add(self.btnNext, span=(1, 1), pos=(9, 3))

        self.btnPause = wx.Button(self, wx.ID_ANY, _(u"暂停"))
        gbSizer1.Add(self.btnPause, span=(1, 1), pos=(9, 6))

        self.btnEnd = wx.Button(self, wx.ID_ANY, _(u"结束答题"))
        gbSizer1.Add(self.btnEnd, span=(1, 1), pos=(9, 8))
        #################################################################
        self.SetSizer(gbSizer1)
        self.Layout()

        self.Centre(wx.BOTH)
        # 添加事件
        self.btnStart.Bind(wx.EVT_BUTTON, self.btnStartOnButtonClick)
        for i in range(1, 6):
            self.creatvar['self.texAns' +
                          str(i)].Bind(wx.EVT_TEXT_ENTER, self.texAnsOnTextEnter)
        self.btnNext.Bind(wx.EVT_BUTTON, self.btnNextOnButtonClick)
        self.btnPause.Bind(wx.EVT_BUTTON, self.btnPauseOnButtonClick)
        self.btnEnd.Bind(wx.EVT_BUTTON, self.btnEndOnButtonClick)

        # 初始化记录
        content = readFile()
        if content:
            self.labRatio.SetLabel(_(u'正确|总数') + ': ' + content)
        else:
            self.labRatio.SetLabel(_(u'当前无记录'))

    def __del__(self):
        pass

    def btnStartOnButtonClick(self, event):
        for i in range(1, 6):
            self.creatvar['self.texAns' + str(i)].Enable()
            tmp = initFix()
            self.creatvar['self.labQues' +
                          str(i)].SetLabel("".join(printFix(tmp)))
            PostfixExp = changeToPostfix(tmp)
            self.res.append(PostfixExp)
        self.eve.set()
        t = threading.Thread(target=self.stopwatch, name='timer')
        t.start()
        self.btnStart.Disable()

    def texAnsOnTextEnter(self, event):
        tex = event.GetEventObject()
        value = tex.GetValue()
        index = tex.GetId()
        cor = CalculatePostfix(self.res[index])
        if value == str(cor):
            self.creatvar['self.labCor' + str(index + 1)].SetLabel(_(u'正确'))
            self.ratio[0] += 1
            self.ratio[1] += 1
            self.labRatio.SetLabel(
                _(u'正确|总数') + ':' + str(self.ratio[0]) + '|' + str(self.ratio[1]))
        else:
            self.creatvar['self.labCor' +
                          str(index + 1)].SetLabel(_(u'错误,正确答案是') + str(cor))
            self.ratio[1] += 1
            self.labRatio.SetLabel(
                _(u'正确|总数') + ':' + str(self.ratio[0]) + '|' + str(self.ratio[1]))
        tex.Disable()

    def btnNextOnButtonClick(self, event):
        self.res = []
        for i in range(1, 6):
            tmp = initFix()
            self.creatvar['self.labQues' +
                          str(i)].SetLabel("".join(printFix(tmp)))
            PostfixExp = changeToPostfix(tmp)
            self.res.append(PostfixExp)
            self.creatvar['self.texAns' + str(i)].Enable()
            self.creatvar['self.labCor' + str(i)].SetLabel('')
            self.creatvar['self.texAns' + str(i)].SetValue('')

    def btnPauseOnButtonClick(self, event):
        if self.btnPause.GetLabel() == _(u'暂停'):
            self.eve.clear()
            self.btnPause.SetLabel(_(u'开始'))
        else:
            self.eve.set()
            self.btnPause.SetLabel(_(u'暂停'))

    def btnEndOnButtonClick(self, event):
        self.eve.clear()
        writeFile(regularizeData(self.ratio))
        dlg = wx.MessageDialog(None, _(u"您的记录已保存"), _(u"感谢使用"),
                               wx.OK | wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_OK:
            self.Close(True)
        dlg.Destroy()

    def stopwatch(self):  # 计时器
        second = 0
        minute = 0
        hour = 0
        while 1:
            if not self.eve.isSet():
                continue
            second += 1
            time.sleep(1)
            if second == 60:
                minute += 1
                second = 0
                if minute == 60:
                    hour += 1
                    minute = 0
                    second = 0
            ntime = "%d:%d:%d" % (hour, minute, second)
            self.labTime1.SetLabel(ntime)


app = wx.App(False)
frame = MyFrame1(None)
frame.Show(True)
app.MainLoop()

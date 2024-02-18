#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re

# class BdbkParseError(Exception):
#     print("BdbkParseError: The content you are looking for cannot be found on the page.It may be because: 1. The word is incorrect and may not be in the Baidu Encyclopedia database. 2. The program itself has an error in parsing. 3. The format of the page content has changed. 4. An unexpected error occurred during the request process. 5. Other unknown unexpected errors. If it is not due to usage, please contact the developer")
#     print("百度百科解析错误：在页面中找不到您想要的内容。可能是因为： 1.这个词不正确，也许不在百度百科数据库中。 2.程序本身解析有误。 3.页面内容格式已有变化。 4.请求过程出现意外错误。 5.其他未知的意外错误。如果非使用原因，清联系开发者")

def meanAgree(text,lang='zh-cn'):
    zh_cn_list = ["是的", "是", "同意", "对", "没错", "正是", "正合我意", "非常同意", "完全同意", "绝对同意", "非常赞同", "我同意", "我支持", "赞同", "对啊", "就是这样", "完全正确", "没错儿", "嗯", "对对", "就是那样", "完全同意你的观点", "哇，这说得对", "对哩，我完全同意", "是呀，说得一点也没错", "对啊对啊，就这么回事儿", "哼唧，完全正确", "嗯呐，完全同意", "哼哈，你说得对极了", "得啦，我跟你站一边儿", "哎呦，这个可以有", "中", "是哩", "对哩", "没错哩", "没叉哩", "实在是中", "没毛病", "没问题", "实对", "实对哩", "实实对哩", "实实是对哩", "一点儿也没问题", "一点儿也没毛病", "可对哩", "可是对哩", "真是对哩", "真对", "可真对", "对着哩", "对们", "对的了"]
    en_list = ["Yes", "OK", "Agree", "Correct", "True", "Absolutely", "Exactly", "I couldn't agree more", "I fully agree with you", "I absolutely agree with you", "I strongly agree with you", "I totally agree with you", "I second that motion", "I'm in agreement with you on that point", "I agree with your viewpoint", "You got it right", "That's spot on", "That's correct", "Correctamundo", "Yep", "Yup", "That's the ticket", "I couldn't agree more with you there", "I fully support your idea/proposal/motion/decision/plan/vision/position/viewpoint/argument/standpoint/conviction/decision/theory/hypothesis/conclusion/proposition/plan/motion/decision/plan/vision/position/viewpoint/argument/standpoint/conviction/decision/theory/hypothesis/conclusion/proposition", "Yer right, I'm with you all the way", "Aye, ye got it spot on", "Aw yeah, couldn't be more right", "Absolutely bang on, mate", "Dang, you're dead-on, partner", "I'm all for it", "You got it", "That's the ticket", "Yeah", "You're right"]
    if lang=="zh-cn":
        if text in zh_cn_list:
            return True
        else:
            return False
    elif lang=="en":
        if text in en_list:
            return True
        else:
            return False

def bdbk(word, id=None, mu_first=False):
    if id != None:
        bdbk_page = requests.get("https://baike.baidu.com/item/%s/%s"%(word,id))
    else:
        bdbk_page = requests.get("https://baike.baidu.com/item/%s"%word)
    
    bdbk_html = bdbk_page.content
    bdbk_bs4 = BeautifulSoup(bdbk_html, 'lxml')
    bdbk_result = bdbk_bs4.find_all("meta")

    if bdbk_result[3]["content"] == "百度百科是一部内容开放、自由的网络百科全书，旨在创造一个涵盖所有领域知识，服务所有互联网用户的中文知识性百科全书。在这里你可以参与词条编辑，分享贡献你的知识。":
        bdbk_multimeanings = []
        for bdbk_multimeaning in bdbk_bs4.find_all("a", re.compile("contentItemChild")):
            bdbk_multimeanings.append({"meaning": bdbk_multimeaning.find("span", re.compile("contentItemChildText")).string, "id": bdbk_multimeaning["href"].split("/")[3].split("?")[0]})
        if mu_first:
            bdbk_html = requests.get("https://baike.baidu.com/item/%s/%s"%(word,bdbk_multimeanings[0]["id"])).content
            bdbk_bs4 = BeautifulSoup(bdbk_html, 'lxml')
            bdbk_result = bdbk_bs4.find_all("meta")
            return {"status": "OK", "id": bdbk_bs4.find("link")["href"].split("/")[5], "description": bdbk_result[3]["content"], "contents": bdbk_result[4]["content"].split(", "), "contents_len": len(bdbk_result[4]["content"].split(", "))}
        else:
            return {"status": "MU", "bdbk_multimeanings": bdbk_multimeanings}
    else:
        return {"status": "OK", "id": bdbk_bs4.find("link")["href"].split("/")[5], "description": bdbk_result[3]["content"], "contents": bdbk_result[4]["content"].split(", "), "contents_len": len(bdbk_result[4]["content"].split(", "))}
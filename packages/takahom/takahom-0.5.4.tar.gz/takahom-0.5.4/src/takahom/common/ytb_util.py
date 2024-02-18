from __future__ import annotations

import re
from typing import Dict, Iterable, Iterator, Callable, Set, cast
from urllib.parse import urlparse, parse_qsl, urlencode

from dknovautils import AT, DkFile, iprint_warn, iprint_info, iprint_debug

from .common_util import CommonUtil, ln_filter_nor_comments_nor_empty
from .down_result import DownResult
from .entity import YtbId, IYtbItem, YtbItem
from .common_ctts_ytb import ytb_url_prefix_www_youtube_com, ytb_code_len_a_11, ytb_reg_simple_code11, \
    YtbConf, \
    ytb_reg_simple_shorts, ytb_url_prefix_www_youtube_com_watch, ytb_reg_simple_id_all, ytb_reg_simple_myid_all
from .common_etc import DkFile2, AT2, f_simple_limiter

from pyrate_limiter import Duration, Rate, Limiter
from flask import Flask, request
import flask

from .common_imports import *


class YtbUtil:

    @staticmethod
    def ytb_check_is_myid(id: str) -> bool:
        assert re.fullmatch(ytb_reg_simple_myid_all, id), 'err95031'
        return "_" not in id

    @staticmethod
    def ytb_check_is_original_id(id: str) -> bool:
        assert re.fullmatch(ytb_reg_simple_id_all, id), 'err95031'
        return "+" not in id

    @staticmethod
    def ytb_original_to_myid(id: str) -> str:
        AT.assert_(YtbUtil.ytb_check_is_original_id(id))
        return id.replace("_", "+")

    @staticmethod
    def ytb_myid_to_original(id: str) -> str:
        AT.assert_(YtbUtil.ytb_check_is_myid(id))
        return id.replace("+", "_")

    @staticmethod
    def ytb_item_check(ytbitem: YtbItem) -> None:
        assert not ytbitem.is_empty(), "err61712"
        url = ytbitem.url
        assert url and len(url) > 10, f"err33528 bad url {url}"
        assert url.startswith(ytb_url_prefix_www_youtube_com), \
            f"err23980 bad url {url}"

        assert 1 == int(ytbitem.has_list()) + int(ytbitem.has_vcode()) + int(ytbitem.has_short()), 'err36996'

        if ytbitem.vcode:
            assert len(ytbitem.vcode) == ytb_code_len_a_11, "err84820 bad v"

        if ytbitem.playlist:
            # list_demo_len = len("PLBSs8pc_eAe5rzljfbZ4qmhQK8eb56pRX")
            _demo_a = 'PLWKjhJtqVAblStefaz+YOVpDWqcRScc2s'
            assert len(_demo_a) == 34
            assert ytb_code_len_a_11 < len(ytbitem.playlist) < len(_demo_a) * 2, \
                f'err78746 length error "{ytbitem.playlist}" '

        if ytbitem.short:
            assert len(ytbitem.short) == ytb_code_len_a_11, "err30341 bad shorts"

    @classmethod
    def parse_ytbid_vcode_from_downloaded_filename(cls, dkf: DkFile | str, ext: str = '.mp4') -> YtbId | None:
        basename = dkf.basename if isinstance(dkf, DkFile) else dkf
        if not basename.endswith(ext):
            return None
        bname = basename[:-len(ext)]  # 去掉 .mp4 字符
        bname = bname[-(ytb_code_len_a_11 + 2):]
        if len(bname) < ytb_code_len_a_11 + 2:
            return None
        # s, *css, e = bname[-(11 + 2):] 不建议对str使用 destructure
        s, css, e = bname[0], bname[1:-1], bname[-1]
        oid = css  # "".join(css)
        ok = (s == '[' and e == ']' and re.fullmatch(ytb_reg_simple_code11, oid))

        if not ok:
            return None
        else:
            r = YtbId(
                prefix=YtbConf.IdPrefix_vcode_ytbid,
                myid=YtbUtil.ytb_original_to_myid(oid),
                id_original=oid)
            return r

    @staticmethod
    def parse_ytbitem_from_url(url: str, silent: bool = False) -> IYtbItem | None:
        """
        支持url中的 v list short 两个参数 其他参数都自动删除

        两个参数不能同时存在 如果同时存在 则作为list处理

        https://www.youtube.com/watch?v=__xx_-xxxxx
        https://www.youtube.com/watch?list=xxxxdfsfsfsdfsfsdfsf
        https://www.youtube.com/watch?v=&list=xxxxdfsfsfsdfsfsdfsf

        https://www.youtube.com/shorts/BrkK9WrcRSQ
        https://www.youtube.com/shorts/BrkK9WrcRSQ?feature=share

        算法

        if url.startswith('xx/shorts'
            short
        elif url.startswith('xx/watch'
            v or list

        """
        try:
            ur = urlparse(url)
            qr = dict(parse_qsl(ur.query))

            def f_url_fullpath(url: str) -> str:
                ur = urlparse(url)
                url2 = ur._replace(query="", fragment="").geturl()
                return url2

            url_full_path = f_url_fullpath(url)
            watch_fullpath = ytb_url_prefix_www_youtube_com_watch == url_full_path

            def f_url2(qr: Dict[str, str]) -> str:
                # [qr.pop(k) for k in list(qr.keys()) if k not in ("v", "list")]
                query2 = urlencode(qr)
                url2 = ur._replace(query=query2, fragment="").geturl()
                return url2

            if re.fullmatch(ytb_reg_simple_shorts, url_full_path):
                scode = ur.path.split('/')[-1]
                assert len(scode) == ytb_code_len_a_11, 'err20039'
                assert YtbConf.short2vcode_将短视频url转换为普通url(), 'err87260'
                ytbitem = YtbItem(
                    url=f"{ytb_url_prefix_www_youtube_com_watch}?v={scode}",
                    vcode=scode,
                    netloc=ur.netloc,
                    url_original=url,
                )
            elif watch_fullpath and qr.get('v', '') and not qr.get('list', ''):
                ytbitem = YtbItem(
                    url=f_url2({'v': qr['v']}),
                    vcode=qr['v'],
                    netloc=ur.netloc,
                    url_original=url,
                )
            elif watch_fullpath and qr.get('v', '') and qr.get('list', ''):
                """
                ?v=tttt&list=xxxx
                """
                url2 = f_url2({'list': qr['list'], 'v': qr['v']})
                ytbitem = YtbItem(
                    url=url2,
                    playlist=qr['list'],
                    netloc=ur.netloc,
                    url_original=url,
                )
            else:
                if not silent:
                    iprint_info(f'err21265 bad url {url} {ur}')
                assert False, 'err57071'

            YtbUtil.ytb_item_check(ytbitem)

        except Exception as e:
            if not silent:
                iprint_info(f"err64022 bad url: {url}")
                iprint_info(e)
            return None

        else:
            return ytbitem

    @staticmethod
    def parse_ytbid_from_url(url: str) -> YtbId | None:
        """
        https://www.youtube.com/watch?v=GVl1E-3FxoQ
        https://www.youtube.com/watch?list=La1CTsdfsdfsdfjpoE_8

        """
        ytbitem = YtbUtil.parse_ytbitem_from_url(url)
        if not ytbitem:
            return None
        assert ytbitem
        ytbid = ytbitem.para_value_to_ytbid()
        return ytbid

    @staticmethod
    def parse_ytbid_from_lines(lns: Iterable[str]) -> Iterator[YtbId]:
        """从多行文本中提取信息

            SA
                去掉注释
                strip not empty

                SB
                    not '.mp4' end
                    start https_ytb_com

                    ytb url
                    get ytbid


                SC
                    not '.mp4' end
                    名称无.符号 ( 这个强化条件 可以排除 其他扩展名）
                    not basename 可以解析dict并且包含 ct r ok
                    匹配id正则表达式
                    len>=11

                    len=11 vcode_original
                    len>11 list_original


                SD
                    来自于 下载数据生成的 目录名称 和 文件名称

                    SDD
                        not '.mp4' end
                        名称无.符号
                        basename 可以解析dict并且包含 ct r ok

                        get ytbid

                    SDF
                        '.mp4' end


                        get ytbid

                    SDS
                        '.description' end

        """

        tprint = AT2.tprint_fun(verbose=False, use_print=True)

        def f_has_folder_keys(ln: DkFile) -> bool:
            return {'ct', 'r', 'ok'}.issubset(CommonUtil.parse_filename_dict(ln, silent=True).keys())

        tprint(f'step45971')

        def handle_ln(ln: str) -> YtbId | None:
            tprint(ln)

            try:
                SA_all = True

                if SB_https := (
                        not ln.endswith('.mp4') \
                        and ln.startswith(ytb_url_prefix_www_youtube_com)
                ):
                    return YtbUtil.parse_ytbid_from_url(ln)
                elif SC_codes := (
                        not ln.endswith('.mp4') \
                        and '.' not in ln \
                        and not f_has_folder_keys(DkFile(ln)) \
                        and re.fullmatch(ytb_reg_simple_id_all, ln) \
                        and len(ln) >= ytb_code_len_a_11
                ):
                    tprint('step15426')
                    YtbUtil.ytb_check_is_original_id(ln)
                    return YtbId(
                        prefix=YtbConf.IdPrefix_vcode_ytbid if len(ln) == ytb_code_len_a_11 \
                            else YtbConf.IdPrefix_list_ytbip,
                        myid=YtbUtil.ytb_original_to_myid(ln),
                        id_original=ln)
                elif SDD_foldername := (
                        not ln.endswith('.mp4') \
                        and '.' not in ln \
                        and f_has_folder_keys(DkFile(ln))
                ):
                    fndc = CommonUtil.parse_filename_dict(DkFile(ln))
                    k = [k for k in fndc.keys() if k in YtbConf.IdPrefixList][0]
                    vstr = f'{k}-{fndc[k]}'
                    return YtbId.build_from_vstr(vstr)
                elif SDF_filename := (
                        ln.endswith('.mp4')
                ):
                    return YtbUtil.parse_ytbid_vcode_from_downloaded_filename(DkFile(ln))
                elif SDS_description := (
                        ln.endswith('.description')
                ):
                    AT.unsupported()
                    return None
                else:
                    return None

            except Exception as e:
                tprint(e)
                return None

        lns = ln_filter_nor_comments_nor_empty(lns)
        rit = (r for ln in lns if (r := handle_ln(ln)))
        return rit

    @staticmethod
    def cal_title_part_from_description_filename(res: DownResult, down_dir: DkFile) -> str | None:
        """
        windows文件名暂时不管
linux文件名最多255bytes
所以 综合按照不超过255字节计算

        字节数量<=240字节计算

        至少存在一个 [xxx].des

102S202 宗教哲學[PLCX-BLZ1hDpCrvRshzjwJllCfqvW9k10n].description

        title长度的确定
            替换._符号
            ct-20230101_r-1111111_ok-yes_ytdip-xxxx

        另外一个可以参考的工具是
        pip install python-slugify

        https://stackoverflow.com/questions/295135/turn-a-string-into-a-valid-filename


        """

        lmt_bytes = res.cal_title_parts_size_lmt()
        assert lmt_bytes > 0

        end_part = f'[{res.req.ytb_ytbid.id_original}].description'
        iprint_debug(f'step96729 {end_part}')
        df = [df
              for df in DkFile2.oswalk_simple_a(down_dir, only_file=True)
              if df.basename.endswith(end_part)
              ]
        if not df:
            return None
        df = df[0]
        name_part = df.basename[:-len(end_part)]

        return YtbUtil.f_cal_chinese_parts(name_part, lmt_bytes)

        # name_part = (name_part.replace(".", "-")  # 替换掉点好 跟文件名好区别
        #              .replace("_", "-"))  # 目录名中不能出现下划线
        # iprint_debug(f'step65880 {name_part}')
        # name_part = YtbUtil.f_trim_by_accumulate(name_part, lmt_bytes, acc_len=lambda c: len(c.encode('utf-8')))
        # max_screen_width = 25 * 2
        # name_part = YtbUtil.f_trim_by_accumulate(name_part, max_screen_width, acc_len=lambda c: 1 if c.isascii() else 2)
        # r = name_part
        # assert len(r.encode('utf-8')) <= lmt_bytes, 'err57430'
        # return r

    @staticmethod
    def f_cal_chinese_parts(name_part: str, lmt_bytes: int, max_screen_width: int = 25 * 2) -> str:

        name_part = (name_part.replace(".", "-")  # 替换掉点好 跟文件名好区别
                     .replace("_", "-"))  # 目录名中不能出现下划线
        iprint_debug(f'step65880 {name_part}')
        name_part = YtbUtil.f_trim_by_accumulate(name_part, lmt_bytes, acc_len=lambda c: len(c.encode('utf-8')))
        # max_screen_width = 25 * 2
        name_part = YtbUtil.f_trim_by_accumulate(name_part, max_screen_width, acc_len=lambda c: 1 if c.isascii() else 2)
        r = name_part
        assert len(r.encode('utf-8')) <= lmt_bytes, 'err57430'
        return r

    @staticmethod
    def f_trim_by_accumulate(s: str, mlmt: int, acc_len: Callable[[str], int]) -> str:
        assert mlmt > 0
        sa = (acc_len(c) for c in s)
        b = ite.accumulate(sa, lambda a, b: a + b)
        b = (i for i, ac in enumerate(b) if ac > mlmt)
        b = list(ite.islice(b, 1))
        i = b[0] if b else None
        if i is None:
            return s
        else:
            return s[:i]

    @staticmethod
    def write_http_resp_a(
            data: bytes | DkFile,
            filename: str,
            content_type: str | None = None,
            content_length: bool = False,
            attachment: bool = True,
            mock_limit: int | None = None,  # 模拟流控
            lower_break_limit: int | None = None,  # 速度低于限制的时候主动停止。
    ) -> Any:
        """
        写这么复杂 是支持两个方面

        模拟限流的效果。服务端进行流控，模拟低速网络。
        检测到超低的下载速度的时候，服务端可以主动停止传送。

        """

        tprint = AT2.tprint_fun(verbose=False)

        tprint("step36815")
        is_file = True if isinstance(data, DkFile) else False
        is_bytes = True if isinstance(data, bytes) else False
        AT.assert_(is_file or is_bytes)

        limiter, tksize = f_simple_limiter(mock_limit) if mock_limit else (None, None)
        lndata = len(cast(bytes, data)) if is_bytes else cast(DkFile, data).filesize

        if not content_type:
            content_type = CommonUtil.MIME_Stream

        resp_paras = {
            "Content-Type": content_type,
            "Content-Length": lndata,
            "Content-Disposition": f'attachment; filename="{filename}"',
        }
        # 不提供length header
        if not content_length:
            del resp_paras["Content-Length"]

        if not attachment:
            del resp_paras["Content-Disposition"]

        start_epoch = AT.fepochSecs()
        sumsize = 0

        time.sleep(0.01)

        def f_too_slow() -> bool:
            SLMT = 30
            if not lower_break_limit:
                return False
            span = AT.fepochSecs() - start_epoch
            if span >= SLMT and sumsize / span < lower_break_limit:
                # todo 记录业务日志
                tprint("step72347 too slow")
                return True
            else:
                return False

        BSIZE = 1024 * 4 * 10

        def f_gen_data_bytes(data: bytes) -> Any:
            nonlocal sumsize
            tprint(f"step99056")
            Step = tksize if tksize else BSIZE
            AT.assert_(Step >= 1, "err97182")
            lndata = len(data)

            i = 0
            while True:
                if i >= lndata:
                    break
                n = min(Step, lndata - i)
                tprint("step96681")
                if limiter:
                    limiter.try_acquire("token")
                r: bytes = data[i: (i + n)]
                sumsize += n
                if f_too_slow():
                    return
                yield r
                tprint(f"step11918 send data {n}")
                i += n

        def f_gen_data_dkfile(data: DkFile) -> Any:
            nonlocal sumsize
            tprint("step65639")
            data: DkFile = data
            rsize = tksize if tksize else BSIZE
            with open(data.pathstr, "rb") as file:
                fi = io.FileIO(file.fileno())
                fb = io.BufferedReader(fi)
                while True:
                    if limiter:
                        limiter.try_acquire("token")
                    r: bytes = fb.read(rsize)
                    if not r:
                        break
                    sumsize += len(r)
                    if f_too_slow():
                        return
                    tprint(f"step33520 yield {len(r)}")
                    yield r

        if isinstance(data, bytes):
            return f_gen_data_bytes(data), resp_paras
        else:
            return f_gen_data_dkfile(data), resp_paras


def cal_v_width(s: str) -> int:
    # non ascii =2 width on screen
    r = sum((1 if c.isascii() else 2) for c in s)
    return r

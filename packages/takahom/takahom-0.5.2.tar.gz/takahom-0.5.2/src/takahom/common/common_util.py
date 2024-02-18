from __future__ import annotations

from .common_imports import *
from .common_etc import AT2, DkFile2


def ln_filter_nor_comments_nor_empty(lns: Iterable[str]) -> Iterator[str]:
    """     每行都strip     去掉空行 #行 -行

    with "#", ";" or "]" are considered as
    comments and ignored

    """
    it = (ln for ln in lns if ln)
    it = AT2.ln_filter_not_startswith(it, ('#', ';', ']'))
    return it


def ln_filter_http_or_https(lns: Iterable[str]) -> Iterator[str]:
    return AT2.ln_filter_startswith(lns, ('http://', 'https://'))


class ChineseCvt(Enum):
    """
    pip install zhconv

    zh-cn 大陆简体
    zh-tw 台灣正體
    zh-hk 香港繁體


    """
    nothing = 0
    # 大陆简体
    zh_cn = 1
    # 台灣正體
    zh_tw = 2
    # 香港繁體
    zh_hk = 3


class CommonUtil:
    MIME_Stream = "application/octet-stream"
    MIME_text_html = "text/html"

    Err_Timeout = "err22603_Msg_timeout"

    special_check_urls_special_100 = [
        "https://totalcommander.ch/1102/tcmd1102x32.exe",
        "https://www.7-zip.org/a/7z2301-x64.exe",
        # 'https://github.com/git-for-windows/git/releases/download/v2.43.0.windows.1/Git-2.43.0-32-bit.exe',
        # 'https://github.com/git-for-windows/git/releases/download/v2.43.0.windows.1/Git-2.43.0-64-bit.exe',
        # 'https://github.com/git-for-windows/git/releases/download/v2.43.0.windows.1/PortableGit-2.43.0-32-bit.7z.exe',
    ]

    special_check_urls_ytb = [
        "https://www.youtube.com/watch?v=ntYmrW6c7GM",
    ]

    special_check_urls = special_check_urls_special_100 + []

    @staticmethod
    def clear_dir(tmp_dir: DkFile) -> None:
        DkFile2.clear_dir(tmp_dir)

    @staticmethod
    def rate_limit(lmts: List[int]) -> int:
        AT.assert_(
            len(lmts) == 24 and all(lm >= 1000 for lm in lmts),
            "err43170 bad rate_limits",
        )
        h = datetime.now().hour
        AT.assert_(0 <= h <= 23)
        return lmts[h]

    @staticmethod
    def test_random_github_url() -> str:
        return (
                CommonUtil.special_check_urls_special_100[0]
                + f"?r={random.randint(10 ** 4, 10 ** 5)}"
        )

    @staticmethod
    def parse_resolution_of_input_filename(dkf: DkFile) -> int | None:
        """
        输入文件的匹配规则
            文件名示例 ytb_xxxx_0720.urls.txt

            文件名不包括 copy 字符串 (因为某些编辑器会临时自动生成这种文件名)
            文件名 ytb_ 开头 .urls.txt结尾
            去掉扩展名 下划线_划分为n部分 n>=2
            s[-1]计算分辨率

            如果只有2部分 则 s[1]计算分辨率

        """
        fname = dkf.basename

        if "copy" not in fname and re.fullmatch(reg_ytb_url_txt, fname):
            fns = fname.split(".")[0].split("_")
            AT.assert_(len(fns) >= 2, f"err50751 bad filename {dkf.pathstr}")
            r = int(fns[-1])
            AT.assert_(240 <= r <= 2500, f"err87022 bad res {dkf.pathstr}")
            return r
        else:
            return None

    @staticmethod
    def url_simple_meta(url: str) -> str:
        # urlinfo = DLCommon.url_simple_meta(url) # 0-9a-zA-Z
        ptn = r"[^0-9a-zA-Z]+"
        url = re.sub(ptn, "-", url)[:70]
        return url

    @staticmethod
    def parse_urls_from_sinput_text(txt: str) -> Iterator[str]:
        return CommonUtil.parse_urls_from_txt(txt)

    @staticmethod
    def parse_urls_from_txt(txt: str) -> Iterator[str]:
        """
        每行去掉头尾空白
        移除 # - 开头的行
        行内 用空白符分割，取0索引部分
        该部分用 urlparser解析，获取url正常 则作为正常url返回

        """
        from urllib.parse import urlparse

        lns = txt.strip().splitlines()
        lns = ln_filter_nor_comments_nor_empty(lns)
        lns = (ln.split(" ")[0] for ln in lns)
        d = {ln: None for ln in lns}
        lns = list(d.keys())

        for ln in lns:
            rp = urlparse(ln)
            if rp.scheme and rp.netloc:
                yield ln

    @staticmethod
    def dir_has_filename(d: DkFile, fname: str) -> bool:
        p = join(d.pathstr, fname)
        p = DkFile(p)
        return p.exists() and p.is_file()

    @staticmethod
    def parse_filename_dict(df: DkFile | str, check: bool = False, silent: bool = False) -> Dict[str, str]:
        """
        如果发生格式错误 将返回空集

        """
        d: Dict[str, str] = {}
        try:
            basename = df.basename if isinstance(df, DkFile) else df.strip()
            bname = basename.split(".")[0]
            bks = (x for x in bname.split("_") if x)  # 防止头部和尾部的_符号造成的空字符串
            for kv in bks:
                ks = kv.split("-")
                _ok = len(ks) >= 2 and len(ks[0]) > 0
                if not _ok:
                    if silent:
                        return {}
                    else:
                        assert False, f"err82633 {ks} {df}"
                k = ks[0]
                v = kv[len(k) + 1:]
                d[k] = v

            if check:
                dc = d
                dcok = dc["ln"] and dc["md5"] and dc["epoch"]
                AT.assert_(dcok, "err48065")

            return d
        except Exception as e:
            if silent:
                iprint_debug(e)
                return {}
            else:
                raise e

    @staticmethod
    def parse_rate_limits_from_conf(s: str) -> List[int]:
        return CommonUtil.parse_rate_limits_from_conf3(s)

    @staticmethod
    def parse_rate_limits_from_conf3(rates_conf: str) -> List[int]:
        """

网速的设置方法
    用逗号分成segment 星号匹配所有小时 0-3表示0,1,2,3一共4个小时的区间
    不同的segment 如果重复定义 以前面的优先级最高
    8:23424,0-3:32424,4-6:234324234,*:3242424

        """

        def pa(s: str) -> Dict[int, int]:

            def mint(s: str) -> int:
                s = int(s.strip())
                assert 0 <= s < 24, f'err91030 bad hour {s}'
                return s

            s = s.strip()
            hp, rate = s.split(':')
            hp = hp.strip()
            rate = int(rate)
            assert 3000 <= rate, f'err53866 need rate >= 3000. bad rate {rate}'

            hs = []
            if hp == '*':
                hs = list(range(0, 24))
            elif '-' not in hp:
                hs = [mint(hp)]
            elif '-' in hp:
                ha, hb = [mint(x) for x in hp.split('-')]
                assert ha <= hb, f'err34531 bad hour {hp}'
                hs = list(range(ha, hb + 1))
            else:
                assert False, f'err89451 bad hour {hp}'

            return {h: rate for h in hs}

        rates_conf = rates_conf.strip()
        LMT = 1000 * 1000 * 10
        dc = {k: LMT for k in range(0, 24)}
        dcs = [pa(p2) for p in rates_conf.split(',') if (p2 := p.strip())]
        for d in reversed(dcs):
            dc.update(d)
        return list(dc.values())

    @staticmethod
    def chinese_cvt_str(fname: str, cvt: ChineseCvt) -> str:
        import zhconv  # type:ignore
        if cvt == ChineseCvt.nothing:
            return fname
        mdict = {
            ChineseCvt.zh_cn: 'zh-cn',
            ChineseCvt.zh_tw: 'zh-tw',
            ChineseCvt.zh_hk: 'zh-hk',
        }

        assert len(mdict) + 1 == len(list(ChineseCvt))
        r = cast(str, zhconv.convert(fname, mdict[cvt]))
        return r

    @staticmethod
    def chinese_convert_directory(pdir: DkFile, cvt: ChineseCvt) -> None:
        """
        将pdir目录下（包括该目录）的所有文件名，包括目录名，都进行重命名
        buttoneup的方式遍历，用rename

import zhconv
text = '便纵有千种风情，更与何人说？'
text1 = zhconv.convert(text, 'zh-hant')

        """

        cnt = 0

        def fcvt(dkf: DkFile, cvt: ChineseCvt) -> None:
            h, t = os.path.split(dkf.path)
            bn = dkf.basename
            bn2 = CommonUtil.chinese_cvt_str(bn, cvt)
            if bn != bn2 and not DkFile(join(h, bn2)).exists():
                os.rename(dkf.pathstr, join(h, bn2))
                nonlocal cnt
                cnt += 1

        for dkf in DkFile2.oswalk_simple_a(pdir, topdown=False):
            fcvt(dkf, cvt)

        if cnt:
            iprint_info(f'convert chinese {cnt}')

    @staticmethod
    def _fcvt(dkf: DkFile, fname: Callable[[DkFile], str]) -> DkFile | None:
        h, t = os.path.split(dkf.path)
        bn = dkf.basename
        bn2 = fname(dkf)
        ndkf = DkFile(join(h, bn2))
        if bn != bn2 and not ndkf.exists():
            os.rename(dkf.pathstr, join(h, bn2))
            return ndkf
        return None

    @staticmethod
    def dir_replace_filename_comma(pdir: DkFile) -> None:
        """
        将所有文件名中的逗号替换为-
        """
        for dkf in DkFile2.oswalk_simple_a(pdir):
            CommonUtil._fcvt(dkf, lambda dkf: dkf.basename.replace(',', '-'))

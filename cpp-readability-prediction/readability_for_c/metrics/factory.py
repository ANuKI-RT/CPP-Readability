from typing import Dict, List

from code_processing.analyzer import CodeAnalyzer
from code_processing.lexer import Lexer, CachedLexer
from metrics import dorn, buse_weimer, itid_nm_nmi, cic, cr, noc, tc, posnett
from metrics.feature_calculator import FeatureCalculator


def get_all_feature_calculators(code: str, language: str) -> Dict[str, FeatureCalculator]:
    analyzer = CodeAnalyzer.create_analyzer(language)
    lexer = CachedLexer(Lexer.create_lexer(language))

    results = {}
    results.update(buse_weimer.get_all_feature_calculators(code, lexer, analyzer=analyzer))
    results.update(dorn.get_all_feature_calculators(code, lexer, analyzer=analyzer))
    results.update(posnett.get_all_feature_calculators(code, lexer))
    results.update(itid_nm_nmi.get_all_feature_calculators(code, analyzer=analyzer))
    results.update(cic.get_all_feature_calculators(code, analyzer=analyzer))
    results.update(cr.get_all_feature_calculators(code, analyzer=analyzer))
    results.update(noc.get_all_feature_calculators(code, analyzer=analyzer))
    results.update(tc.get_all_feature_calculators(code, lexer, analyzer=analyzer))

    return results


def get_all_metrics() -> List[str]:
    return list(get_all_feature_calculators('', 'cpp').keys())

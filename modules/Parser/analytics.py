from modules.Parser import RequestResult


class RequestStatsAnalyzer:

    def __init__(self, result_list: list[RequestResult]) -> None:
        self.result_list = result_list

    @property
    def avg_time(self, exclude_bad: bool = True) -> float:
        rsl = self.result_list
        if exclude_bad:
            rsl = list(filter(lambda rs: rs.status != 0, rsl))
        return sum(rs.time for rs in rsl) / len(rsl)

    @property
    def avg_size(self) -> int:
        rsl = list(filter(lambda rs: rs.status != 0, self.result_list))
        return int(sum(rs.size for rs in rsl) / len(rsl))

    @property
    def majority_n_links(self) -> int:
        rsl = list(filter(lambda rs: rs.status != 0, self.result_list))
        nll = [rs.n_matches for rs in rsl]
        return sorted(
            [(nl, nll.count(nl)) for nl in set(nll)],
            key=lambda tpl: tpl[1],
            reverse=True,
        )[0][0]

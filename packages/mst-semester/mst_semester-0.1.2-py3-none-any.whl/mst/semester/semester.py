from dataclasses import dataclass
from typing import List, Literal, Tuple, Optional, Union
import datetime
import json
import platform
import pwd
import os
import re
import time
import requests
from mst.core import LogAPIUsage, local_env


@dataclass
class SchoolTerm:
    """Response from mstcoresem"""

    term: str
    strm: str
    date_begin: str
    date_end: str
    deadweek_begin: str
    deadweek_end: str
    finals_begin: str
    finals_end: str

    def next_term(self):
        try:
            return Semester().get_adjacent_term(
                strm=self.strm, term_format="object", direction="next"
            )
        except RuntimeError:
            # Could not find next term
            return None

    def previous_term(self):
        try:
            return Semester().get_adjacent_term(
                strm=self.strm, term_format="object", direction="previous"
            )
        except RuntimeError:
            # Could not find previous term
            return None


class Semester:
    """
    Background and restrictions:

        The University of Missouri implemented the PeopleSoft Student Database,
        at the Rolla campus, in January 2004.  The word "semester" is not used
        in the University's implementation of PeopleSoft; the proper word to
        use is "term".

        The session term (strm) is always a character string composed of only
        digits with a length = 4.  The first two digits map to a calendar year.
        Since January 1996, the last two digits map to a specific strm within
        that calendar year.  The most important session term codes (as of the
        March 2013 version of the script) used by the Rolla campus are:
        27 = Spring, 35 = Summer and 43 = Fall.  Spring and Fall terms are 16
        weeks; Summer is 8 weeks. For terms since January 1996, adding 197200
        to the strm value will produce the Rolla internal term (YYYYTT),
        where YYYY is the calendar year and TT is 27, 35 or 43.

        The Missouri S & T implementation for the value of strm (session term)
        has these restrictions:
        1.  Since it is possible that the scheme used for the strm could change
            at any time, this module may need to be significantly updated
            *and/or* deprecated, then finally decommissioned.
        2.  The strm value has an irregular pattern prior to 1996.  Dates prior
            to December 16, 1995 will fail when used with this module.
        3.  The strm will not properly work beyond the year 2071
            (strm = 9927, which represents term Spring 2071).
        4.  Generally speaking, the pre-1996 terms have some non-PK columns
            that are inconsistent or unreliable.
        5.  Terms that are more than about 1-2 years in the future do not have
            reliable start and end dates. This is the reason why we have to
            receive permision from the registrar to copy term data into this
            module at least once each year.
    """

    school_terms: List[SchoolTerm]

    # Give names to specific useful dates in the SCHOOL TERMS array
    last_date_term_zero = None
    first_date_available = None
    last_date_available = None

    @staticmethod
    def _init_cachefile() -> Tuple[Optional[str], str]:
        """Initalize the cachefile

        Returns:
            Tuple[Optional[str], str]: directory and filename for cache in list context
        """
        cache = None
        home = pwd.getpwuid(os.geteuid())[5]

        if os.path.isdir(home):
            cache = f"{home}/tmp/core-sem-cache"
            os.makedirs(cache, mode=0o700, exist_ok=True)
        elif (
            platform.system() == "Windows"
            and os.getenv("TEMP")
            and "docum" in os.getenv("TEMP").lower()
        ):
            cache = f'{os.getenv("TEMP")}/core-sem-cache'
            os.makedirs(cache, mode=0o700, exist_ok=True)

        return (cache, f"{cache}/semesters.json")

    def __init__(self) -> None:
        env = local_env()
        env_suffix = "" if env == "prod" else f"-{env}"

        rpchost = f"mstcoresem.apps{env_suffix}.mst.edu"
        location = f"https://{rpchost}/cgi-bin/cgiwrap/mstcoresem/json-semesters.pl"

        sem_text = ()
        cache, cachefilename = self._init_cachefile()
        if cache:
            ttl = 6 * 60 * 60

            ctime = 0
            mtime = 0
            try:
                tmpstat = os.stat(cachefilename)
                ctime = tmpstat.st_ctime
                mtime = tmpstat.st_mtime
            except FileNotFoundError:
                # This means the cache file has not been made; the defaults will trigger an update.
                pass

            if not (time.time() - ctime < 30 or time.time() - mtime < ttl):
                data = requests.get(location, timeout=120).text
                with open(cachefilename, "w", encoding="utf8") as cfh:
                    cfh.write(data)

            if os.path.isfile(cachefilename):
                with open(cachefilename, "r", encoding="utf8") as cfh:
                    sem_text = cfh.read()

        if not sem_text:
            sem_text = requests.get(location, timeout=120).text

        core_sem_data = json.loads(sem_text)
        if not core_sem_data:
            core_sem_data = {"data": []}
            if cache:
                os.remove(cachefilename)

        self.school_terms = []
        for rec in core_sem_data["data"]:
            self.school_terms.append(
                SchoolTerm(
                    term=rec["term"],
                    strm=rec["strm"],
                    date_begin=rec["date_begin"],
                    date_end=rec["date_end"],
                    deadweek_begin=rec["deadweek_begin"],
                    deadweek_end=rec["deadweek_end"],
                    finals_begin=rec["finals_begin"],
                    finals_end=rec["finals_end"],
                )
            )

        self.last_date_term_zero = self.school_terms[0].date_end
        self.first_date_available = self.school_terms[1].date_begin
        self.last_date_available = self.school_terms[-1].date_end

    def get_school_term(
        self,
        search_date: str = None,
        between_terms: Literal["next", "previous", "ignore"] = "next",
        term_format: Literal[
            "description", "peoplesoft", "legacy", "object"
        ] = "description",
    ) -> Union[int, str, SchoolTerm, None]:
        """Outputs a school term found by the parameters in the requested format
        Args:
            search_date (str, optional): If not provided, search date will default to current date.
                The search date parameter must have the format YYYY-MM-DD.
                The function will use this parameter to determine which
                term was/is/will be in session on the search date.
            between_terms (str, optional): If not provided, between_terms will default to 'next'.
                The between_terms parameter determines what to do when the
                search date falls *BETWEEN* terms.  This parameter is only
                used when search date falls outside of the range defined by
                the start and end dates of every term; otherwise, it has no
                meaning.
                Valid values and corresponding result are shown:
                VALUE       RESULTING ACTION
                ----------  ----------------------------------
                'next'      the next term will be returned
                'previous'  the previous term will be returned
                'ignore'    an empty string will be returned
                None        the next term will be returned

            term_format (str, optional): If not provided, term_format will default to 'description'.
                The term_format parameter determines the format of the
                returned value.  If term_format is 'legacy', the internal
                Rolla term code will be returned as six-digits using the
                Oracle data type VARCHAR2(6).  The format is YYYYTT where
                YYYY is the calendar year and TT represents the term:
                    27 = Spring, 35 = Summer, 43 = Fall
                Valid values and corresponding result are shown:
                VALUE          RESULTING ACTION
                -------------  ----------------------------------
                'description'  PS_TERM_TBL.DESCRSHORT will be returned
                'peoplesoft'   PS_TERM_TBL.STRM will be returned
                'legacy'       internal Rolla term code will be returned
                'object'       Returns a SchoolTerm object
                None           PS_TERM_TBL.DESCRSHORT will be returned

                IMPORTANT:  It is strongly recommended that no dependencies be
                            built into any script based on the DESCRIPTION value.
                            There is no guarantee that the description will have
                            any kind of predictable format.  Description should
                            only be used for DISPLAY PURPOSES!

        Raises:
            ValueError: Invalid search date month
            ValueError: Invalid search date day
            ValueError: Invalid search date day for month
            ValueError: Search date too early
            ValueError: Search date too late
            ValueError: Term information not availble for search date
            ValueError: Term information not yet availble for search date
            ValueError: Invalid search date format. Must be YYYY-MM-DD
            ValueError: Invalid between terms option
            ValueError: Invalid term format option
            RuntimeError: Term data missing
            RunTimeError: Invalid PS term format
            RunTimeError: PS term prior to available terms
            RunTimeError: PS term after available terms
            RunTimeError: PS term invalid
            RunTimeError: Term description invalid
            RunTimeError: Internal term invalid


        Returns:
            Union[int, str, SchoolTerm, None]: A code, description, or SchoolTerm instance of a term
        """
        LogAPIUsage()

        if search_date is None:
            search_date = datetime.date.today().isoformat()

        date_9_days_earlier = None

        # Validate search date param
        # Done manually since datetime's exceptions can be unclear.
        if len(search_date) == 10 and re.search(r"^\d{4}-\d{2}-\d{2}$", search_date):
            year, month, day = (int(x) for x in search_date.split("-"))

            if month < 1 or month > 12:
                raise ValueError(
                    f"Invalid search date month {month} (must be YYYY-MM-DD): {search_date}"
                )
            if day < 1 or day > 31:
                raise ValueError(
                    f"Invalid search date day {day} (must be YYYY-MM-DD): {search_date}"
                )
            if day > 28:
                try:
                    datetime.datetime.strptime(search_date, "%Y-%m-%d")
                except ValueError as exc:
                    raise ValueError(
                        f"Invalid search date day {day} for the specified month {month}: {search_date}"
                    ) from exc
            elif search_date < self.last_date_term_zero:
                last_date = datetime.datetime.strptime(
                    self.last_date_term_zero, "%Y-%m-%d"
                )
                last_date += datetime.timedelta(days=1)
                last_date_fmt = last_date.strftime("%B %d, %Y")
                raise ValueError(
                    f"This function cannot process dates prior to {last_date_fmt}: {search_date}"
                )
            elif year > 2071:
                raise ValueError(
                    f"This function cannot process dates after the year 2071: {search_date}"
                )
            elif search_date < self.first_date_available:
                if between_terms != "next":
                    raise ValueError(
                        f"Term information is not available for this date: {search_date}"
                    )
            elif search_date > self.last_date_available:
                emsg = f"Term information is not yet available for this date: {search_date}"
                if between_terms != "previous":
                    raise ValueError(emsg)
                else:
                    date_9_days_earlier = datetime.datetime.strptime(
                        search_date, "%Y-%m-%d"
                    ) - datetime.timedelta(days=9)
                    date_9_days_earlier = date_9_days_earlier.date().isoformat()
                    if date_9_days_earlier > self.last_date_available:
                        raise ValueError(f"The {emsg}")
        else:
            raise ValueError(
                f"Invalid search date format. (Must be YYYY-MM-DD): {search_date}"
            )

        if between_terms not in ("next", "previous", "ignore"):
            raise ValueError(f"Invalid between terms option: {between_terms[:30]}")
        if term_format not in ("description", "peoplesoft", "legacy", "object"):
            raise ValueError(f"Invalid term format option: {term_format[:30]}")

        (ps_term, prior_term, follow_term) = self._find_term_by_date(
            search_date, between_terms, date_9_days_earlier
        )

        if between_terms == "ignore":
            if not (
                ps_term
                or ps_term.term
                or ps_term.strm
                or ps_term.date_begin
                or ps_term.date_end
            ):
                return None

        if not ps_term:
            if between_terms == "previous":
                ps_term = prior_term
            elif between_terms == "next":
                ps_term = follow_term

        # If any of these are missing, that's an error
        if not (
            ps_term.term and ps_term.strm and ps_term.date_begin and prior_term.date_end
        ):
            raise RuntimeError(
                f"ERROR: Term data is missing using {search_date} / {between_terms} (values returned: {ps_term.term[:50]}, {ps_term.strm[:30]}, {ps_term.date_begin[:30]}, {ps_term.date_end[:30]})"
            )

        ps_term.strm: str
        if len(ps_term.strm) != 4 or not re.search(r"^\d{4}$", ps_term.strm):
            raise RuntimeError(
                f"ERROR: The PS term has an invalid format (value returned: {ps_term.strm[:30]})"
            )
        if ps_term.strm < "2427":
            raise RuntimeError(
                f"ERROR: Term {ps_term.strm} is prior to the available terms using {search_date} / {between_terms}."
            )
        if ps_term.strm > "9927":
            raise RuntimeError(
                f"ERROR: Term {ps_term.strm} is after the available terms using {search_date} / {between_terms}."
            )
        if not re.search(r"^\d{2}(27|35|43)$", ps_term.strm):
            raise RuntimeError(
                f"ERROR: Term {ps_term.strm} format is invalid using {search_date} / {between_terms}."
            )

        descr_len = len(ps_term.term)
        if descr_len < 4 or descr_len > 30:
            raise RuntimeError(
                f"ERROR: Term description length is invalid using {search_date} / {between_terms}. (length={descr_len}, value returned: {ps_term.term[:50]})"
            )

        term_internal = int(ps_term.strm) + 197200
        if term_internal < 199627 or term_internal > 207127:
            raise RuntimeError(
                f"ERROR: Internal term is invalid using {search_date} / {between_terms}. (value={term_internal})"
            )

        match term_format:
            case "description":
                return ps_term.term
            case "peoplesoft":
                return ps_term.strm
            case "object":
                return ps_term
            case _:
                return term_internal

    def get_adjacent_term(
        self,
        strm: str = None,
        search_date: str = None,
        between_terms: Literal["next", "previous"] = "next",
        term_format: Literal[
            "description", "peoplesoft", "legacy", "object"
        ] = "peoplesoft",
        direction: Literal["next", "previous"] = "next",
    ) -> Union[int, str, SchoolTerm]:
        """Grabs term adjacent to supplied strm, if no strm is supplied - uses "current" strm

        Args:
            strm (str, optional): grab term adjacent to supplied strm, if no strm is supplied get_adjacent_term will
                try to guess the current term using search_date and between_terms keys
                see documentation for get_school_term for more information.
            search_date (str, optional): see documentation for strm
            between_terms (Literal["next", "previous"], optional): see documentation for strm
            term_format (Literal["peoplesoft", "description", "legacy"], optional): which format to return results as. Valid values as follows:
                peoplesoft - (default) ps_term_tbl.strm will be returned
                description - ps_term_tbl.descrshort will be returned
                legacy - internal Rolla term code will be returned.
                object - a SchoolTerm instance will be returned
            direction (Literal["next", "previous"], optional): which adjacent term to grab. Valid values as follows:
                next - term after supplied strm will be returned
                previous - term before supplied strm will be returned.

        Raises:
            ValueError: Invalid term format
            ValueError: Invalid direction
            RuntimeError: Cannot find adjacent term

        Returns:
            Union[int, str]: scalar value on success, undef on error (Check $MST::Core::Semester::ErrorMsg for more information)
        """
        LogAPIUsage()

        if term_format not in ("peoplesoft", "description", "legacy", "object"):
            raise ValueError(f"ERROR: Invalid term format ({term_format})")

        if direction not in ("next", "previous"):
            raise ValueError(
                f"ERROR: get_adjacent_term - invalid direction ({direction})"
            )

        if not strm:
            strm = self.get_school_term(
                search_date=search_date,
                between_terms=between_terms,
                term_format="peoplesoft",
            )

        tgt_idx = -1

        # pylint: disable-next=consider-using-enumerate
        for idx in range(len(self.school_terms)):
            tgt = self.school_terms[idx]

            if tgt.strm == strm:
                if direction == "next":
                    if idx == len(self.school_terms) - 1:
                        tgt_idx = idx
                        break
                    elif self.school_terms[idx + 1]:
                        tgt_idx = idx + 1
                        break
                if direction == "previous" and self.school_terms[idx - 1]:
                    tgt_idx = idx - 1
                    break

        if tgt_idx == -1:
            raise RuntimeError(
                f"ERROR: Unable to locate term adjacent to {strm} ({direction})"
            )

        target = self.school_terms[tgt_idx]

        match term_format:
            case "description":
                return target.term
            case "peoplesoft":
                return target.strm
            case "object":
                return target
            case _:
                return int(target.strm) + 197200

    def get_term_info(self, term: Union[str, int]) -> Optional[SchoolTerm]:
        """Returns a the SchoolTerm instance for the given term

        Args:
            term (Union[str, int]): Either strm or term

        Returns:
            Optional[SchoolTerm]: The requested term or None if no term matches.
        """
        LogAPIUsage()

        for rec in self.school_terms:
            if term in [rec.term, rec.strm]:
                return rec

        return None

    def _find_term_by_date(
        self,
        search_date: str,
        between_terms: Literal["next", "previous", "ignore"],
        date_9_days_earlier: str,
    ) -> Tuple[SchoolTerm, SchoolTerm, SchoolTerm]:
        """Searches for data associated with a date in the school terms list

        Args:
            search_date (str): The date to search for
            between_terms (Literal["next", "previous", "ignore"]): How to handle dates that fall between terms
            date_9_days_earlier (str):

        Raises:
            ValueError: Invalid search date value
            ValueError: Invalid search date format
            ValueError: Search date too far in future

        Returns:
            Tuple[SchoolTerm, SchoolTerm, SchoolTerm]: A tuple of the (current, prior, following) terms.
        """
        LogAPIUsage()

        term_current_data = None  # Current Term
        term_prior_data = None  # Prior Term
        term_following_data = None  # Following Term

        if re.search(r"^\d{4}-\d{2}-\d{2}$", search_date):
            converted_sd = (int(x) for x in search_date.split("-"))
            try:
                datetime.date(*converted_sd)
            except ValueError as exc:
                raise ValueError(
                    f"ERROR_find_term_by_date. Invalid search date: {search_date}"
                ) from exc
        else:
            raise ValueError(
                f"ERROR_find_term_by_date. Invalid search date format. (Must by YYYY-MM-DD): {search_date[:30]}"
            )

        param_9_days_valid = 0

        if search_date > self.last_date_available:
            if between_terms == "previous":
                if re.search(r"^\d{4}-\d{2}-\d{2}$", date_9_days_earlier):
                    converted_9_days = (int(x) for x in date_9_days_earlier.split("-"))
                    try:
                        datetime.date(*converted_9_days)
                    except ValueError:
                        pass

                    if date_9_days_earlier < self.last_date_available:
                        param_9_days_valid = 1

                if not param_9_days_valid:
                    raise ValueError(
                        f"ERROR_find_term_by_date. The search date is too far in the future: {search_date}"
                    )
            else:
                raise ValueError(
                    f"ERROR_find_term_by_date. Search date is too far in the future: {search_date}"
                )

        if search_date > self.last_date_available:
            if (
                between_terms == "previous"
                and param_9_days_valid
                and date_9_days_earlier < self.last_date_available
            ):
                term_prior_data = self.school_terms[-1]
                return term_current_data, term_prior_data, term_following_data

            raise ValueError(
                f"ERROR_find_term_by_date. UNEXPECTED date is too far in the future: {search_date}"
            )

        term_found_status = 0  # 0 = target term not found, 1 = found target term

        for term in self.school_terms:
            if term_found_status:
                if (
                    self.first_date_available <= term.date_begin
                    and self.last_date_available >= term.date_end
                ):
                    term_following_data = term
                break

            if term.date_end >= search_date >= term.date_begin:
                if (
                    self.first_date_available <= term.date_begin
                    and self.last_date_available >= term.date_end
                ):
                    term_current_data = term
                    term_found_status = 1
            else:
                if search_date < term.date_begin:
                    if (
                        self.first_date_available <= term.date_begin
                        and self.last_date_available >= term.date_end
                    ):
                        term_following_data = term
                    break

                if (
                    self.first_date_available <= term.date_begin
                    and self.last_date_available >= term.date_end
                ):
                    term_prior_data = term
        return term_current_data, term_prior_data, term_following_data

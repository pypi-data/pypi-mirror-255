import argparse
import asyncio
from datetime import datetime
import gzip
import io
import json
import os
import sys
from typing import Any, List, Optional

import httpx
import zstandard
from ordered_set import OrderedSet
from pydantic import AliasChoices, BaseModel, Field, JsonValue
from tenacity import retry, stop_after_attempt, wait_exponential
from tqdm import tqdm
from asyncinotify import Inotify, Mask


class OldMetadataConnector(BaseModel):
    minerva_version: Optional[str] = Field(None, alias="minerva_version")
    name: Optional[str] = Field(None, alias="name")


class OldMatchInfo(BaseModel):
    category: Optional[list[str] | str] = Field(None, alias="category")
    category_id: Optional[list[int]] = Field(None, alias="category_id")
    company: Optional[list[str] | str] = Field(None, alias="company")
    company_id: Optional[list[int]] = Field(None, alias="company_id")
    company_main: Optional[list[str] | str] = Field(None, alias="company_main")
    company_main_id: Optional[list[int]] = Field(None, alias="company_main_id")
    country: Optional[list[str] | str] = Field(None, alias="country")
    country_id: Optional[list[int]] = Field(None, alias="country_id")
    country_main: Optional[list[str] | str] = Field(None, alias="country_main")
    country_main_id: Optional[list[int]] = Field(None, alias="country_main_id")
    expressions: Optional[list[str] | str] = Field(None, alias="expressions")
    group: Optional[list[str] | str] = Field(None, alias="group")
    group_id: Optional[list[int]] = Field(None, alias="group_id")
    industrysector: Optional[list[str] | str] = Field(None, alias="industrysector")
    industrysector_id: Optional[list[int]] = Field(None, alias="industrysector_id")
    keyword: Optional[list[str] | str] = Field(None, alias="keyword")
    keyword_id: Optional[list[str]] = Field(None, alias="keyword_id")
    malwarekit: Optional[list[str] | str] = Field(None, alias="malwarekit")
    malwarekit_id: Optional[list[int]] = Field(None, alias="malwarekit_id")
    rules: Optional[list[str] | str] = Field(None, alias="rules")
    source: Optional[list[str] | str] = Field(None, alias="source")
    source_id: Optional[list[int]] = Field(None, alias="source_id")
    technology: Optional[list[str] | str] = Field(None, alias="technology")
    technology_id: Optional[list[int]] = Field(None, alias="technology_id")
    threatactor: Optional[list[str] | str] = Field(None, alias="threatactor")
    threatactor_id: Optional[list[int]] = Field(None, alias="threatactor_id")
    vulnerability: Optional[list[str] | str] = Field(None, alias="vulnerability")
    vulnerability_id: Optional[list[int]] = Field(None, alias="vulnerability_id")
    provider: Optional[list[str] | str] = Field(None, alias="provider")
    provider_id: Optional[list[int]] = Field(None, alias="provider_id")
    attck: Optional[list[str] | str] = Field(None, alias="attck")
    attck_id: Optional[list[int]] = Field(None, alias="attck_id")


class OldMetadata(BaseModel):
    connector: Optional[OldMetadataConnector] = Field(None, alias="connector")
    matchinfo: Optional[OldMatchInfo] = Field(None, alias="matchinfo")
    analysis_id: Optional[str] = Field(None, alias="analysis_id")
    doc_id: Optional[str] = Field(None, alias="doc_id")
    id_: Optional[str] = Field(None, alias="id")
    language: Optional[str] = Field(None, alias="language")
    observation_time: Optional[str] = Field(None, alias="observation_time")
    source: Optional[str] = Field(None, alias="source")
    translation: Optional[str] = Field(None, alias="translation")


class NerEntities(BaseModel):
    event: Optional[str] = Field(None, alias="event")
    gpe: Optional[str] = Field(None, alias="gpe")
    money: Optional[str] = Field(None, alias="money")
    norp: Optional[str] = Field(None, alias="norp")
    org: Optional[str] = Field(None, alias="org")
    person: Optional[str] = Field(None, alias="person")
    product: Optional[str] = Field(None, alias="product")


class OldSystem(BaseModel):
    ttl: Optional[int] = Field(None, alias="TTL")
    first_seen: Optional[str] = Field(None, alias="firstSeen")
    src_chain: Optional[list[str] | str] = Field(None, alias="srcChain")


class OldAttributes(BaseModel):
    domain: Optional[list[str | None]] = Field(None)
    email: Optional[list[str | None]] = Field(None)
    file: Optional[list[str]] = Field(None)
    hostname: Optional[list[str | None]] = Field(None)
    ip: Optional[list[str]] = Field(None)
    ipv4_port: Optional[list[str]] = Field(None, alias="ipv4-port")
    md5hash: Optional[list[str]] = Field(None)
    sha1hash: Optional[list[str]] = Field(None)
    sha256hash: Optional[list[str]] = Field(None)
    url: Optional[list[str] | str] = Field(None)
    author: Optional[str] = Field(None)
    cluster_id: Optional[str] = Field(None)
    ssl_sha1fingerprint: Optional[list[str]] = Field(None, alias="ssl-sha1fingerprint")
    cve: Optional[list[str] | str] = Field(None)


class OldCommon(BaseModel):
    author: Optional[str] = Field(None)


class OldSource(BaseModel):
    timestamp: Optional[str] = Field(None, alias="@timestamp")
    attributes: Optional[OldAttributes] = Field(None, alias="attributes")
    system: Optional[OldSystem] = Field(None, alias="system")
    metadata: Optional[OldMetadata] = Field(None, alias="metadata")
    document: Optional[dict[str, JsonValue]] = Field(None, alias="document")
    common: Optional[OldCommon] = Field(None, alias="common")


class OldDocument(BaseModel):
    index: Optional[str] = Field(None, validation_alias=AliasChoices("_index", "index"))
    type_: Optional[str] = Field(None, validation_alias=AliasChoices("_type", "type"))
    id_: Optional[str] = Field(None, validation_alias=AliasChoices("_id", "id"))
    score: Optional[int] = Field(None, validation_alias=AliasChoices("_score", "score"))
    source: OldSource = Field(validation_alias=AliasChoices("_source", "source"))
    version: Optional[int] = Field(
        None, validation_alias=AliasChoices("_version", "version")
    )
    sort: Optional[list[int | str]] = Field(None)


class NewSystem(BaseModel):
    ttl: Optional[int] = Field(None)
    source: Optional[str] = Field(None)
    previous: Optional[list[str]] = Field(None)
    converted: bool = Field(True)
    converted_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class NewSignalMetadata(BaseModel):
    id: Optional[str] = Field(None)
    version: Optional[int] = Field(None)
    link: Optional[str] = Field(None)
    updated_at: Optional[str] = Field(None)
    published_at: Optional[str] = Field(None)
    ingested_at: Optional[str] = Field(None)


class NewSectionData(BaseModel):
    raw: Optional[JsonValue] = Field(None)
    structured: dict[str, Any] = Field({})


class NewSectionCommon(BaseModel):
    title: Optional[str] = Field(None)
    summary: Optional[str] = Field(None)
    quo_summary: Optional[str] = Field(None)


class NewFile(BaseModel):
    filename: Optional[str] = Field(None)
    sha256: Optional[str] = Field(None)
    description: Optional[str] = Field(None)


class NewSectionEntities(BaseModel):
    author: Optional[list[str]] = Field(None)
    attachment: Optional[list[NewFile]] = Field(None)
    category: Optional[list[str]] = Field(None)
    company: Optional[list[str]] = Field(None)
    cve: Optional[list[str]] = Field(None)
    gpe: Optional[list[str]] = Field(None)
    event: Optional[list[str]] = Field(None)
    norp: Optional[list[str]] = Field(None)
    person: Optional[list[str]] = Field(None)
    product: Optional[list[str]] = Field(None)
    money: Optional[list[str]] = Field(None)
    facility: Optional[list[str]] = Field(None)
    date: Optional[list[str]] = Field(None)


class NewSectionAttributes(BaseModel):
    domain: Optional[list[str]] = Field(None)
    email: Optional[list[str]] = Field(None)
    file: Optional[list[str]] = Field(None)
    hostname: Optional[list[str]] = Field(None)
    ip: Optional[list[str]] = Field(None)
    md5hash: Optional[list[str]] = Field(None)
    sha1hash: Optional[list[str]] = Field(None)
    sha256hash: Optional[list[str]] = Field(None)
    url: Optional[list[str]] = Field(None)
    ccnumber: Optional[list[str]] = Field(None)
    password: Optional[list[str]] = Field(None)


class NewSectionCatalog(BaseModel):
    company: Optional[list[str]] = Field(None)
    company_id: Optional[list[int | str]] = Field(None)
    company_main: Optional[list[str]] = Field(None)
    company_main_id: Optional[list[int]] = Field(None)
    industrysector: Optional[list[str]] = Field(None)
    industrysector_id: Optional[list[int]] = Field(None)
    technology: Optional[list[str]] = Field(None)
    technology_id: Optional[list[int]] = Field(None)
    vulnerability: Optional[list[str]] = Field(None)
    vulnerability_id: Optional[list[int]] = Field(None)
    attck: Optional[list[str]] = Field(None)
    attck_id: Optional[list[int]] = Field(None)
    category: Optional[list[str]] = Field(None)
    category_id: Optional[list[int]] = Field(None)
    country: Optional[list[str]] = Field(None)
    country_id: Optional[list[int]] = Field(None)
    keyword: Optional[list[str]] = Field(None)
    keyword_id: Optional[list[str]] = Field(None)
    malwarekit: Optional[list[str]] = Field(None)
    malwarekit_id: Optional[list[int]] = Field(None)
    provider: Optional[list[str]] = Field(None)
    provider_id: Optional[list[int]] = Field(None)
    persona: Optional[list[str]] = Field(None)
    persona_id: Optional[list[int]] = Field(None)
    source: Optional[list[str]] = Field(None)
    source_id: Optional[list[int]] = Field(None)
    threatactor: Optional[list[str]] = Field(None)
    threatactor_id: Optional[list[int]] = Field(None)


class NewSignal(BaseModel):
    timestamp: str = Field(
        validation_alias=AliasChoices("timestamp", "@timestamp"),
        serialization_alias="@timestamp",
    )
    system: NewSystem = Field()
    metadata: NewSignalMetadata = Field()
    data: NewSectionData = Field()
    common: NewSectionCommon = Field()
    entities: NewSectionEntities = Field()
    attributes: NewSectionAttributes = Field()
    catalog: NewSectionCatalog = Field()
    # translations: Optional[SectionTranslations] = Field(None)


class NewDocument(BaseModel):
    index: Optional[str] = Field(None, alias="_index")
    type_: Optional[str] = Field(None, alias="_type")
    id_: Optional[str] = Field(None, alias="_id")
    score: Optional[int] = Field(None, alias="_score")
    source: NewSignal = Field(alias="_source")
    version: Optional[int] = Field(None, alias="_version")


def as_set(src: List[Any] | Any | None) -> list[str] | None:
    if src is None:
        return None
    if not isinstance(src, list):
        return list(OrderedSet([src]))
    if None in src:
        src.remove(None)
    return list(OrderedSet(src))


def as_list(src: List[Any] | Any | None) -> list[str] | None:
    if src is None:
        return None
    return src if isinstance(src, list) else [src]


def merge_as_set(
    a: List[Any] | Any | None, b: List[Any] | Any | None
) -> List[Any] | None:
    res = as_set(a)
    if res is None:
        res = as_set(b)
    elif set_b := as_list(b):
        res.extend(set_b)
        res = list(OrderedSet(res))
    return res if res is None else list(res)


def convert_doc(msg: OldDocument, index: str = "") -> NewDocument:
    mi = msg.source.metadata.matchinfo if msg.source.metadata else None

    data_raw = None
    if msg.source.document and "raw" in msg.source.document:
        data_raw = msg.source.document["raw"]
        del msg.source.document["raw"]

    signal_id = msg.id_
    if (
        msg.source.metadata
        and msg.source.metadata.id_
        and msg.source.metadata.id_ != ""
    ):
        signal_id = msg.source.metadata.id_

    sig = NewSignal(
        timestamp=msg.source.timestamp,
        attributes=NewSectionAttributes(
            domain=as_set(msg.source.attributes.domain),
            email=as_set(msg.source.attributes.email),
            file=as_set(msg.source.attributes.file),
            hostname=as_set(msg.source.attributes.hostname),
            ip=as_set(msg.source.attributes.ip),
            md5hash=as_set(msg.source.attributes.md5hash),
            sha1hash=merge_as_set(
                msg.source.attributes.sha1hash,
                msg.source.attributes.ssl_sha1fingerprint,
            ),
            sha256hash=as_set(msg.source.attributes.sha256hash),
            url=as_set(msg.source.attributes.url),
        )
        if msg.source.attributes
        else NewSectionAttributes(),
        catalog=NewSectionCatalog(
            attck=as_set(mi.attck),
            attck_id=as_set(mi.attck_id),
            category=as_set(mi.category),
            category_id=as_set(mi.category_id),
            company=merge_as_set(mi.company, mi.group),
            company_id=merge_as_set(mi.company_id, mi.group_id),
            company_main=as_set(mi.company_main),
            company_main_id=as_set(mi.company_main_id),
            country=as_set(mi.country),
            country_id=as_set(mi.country_id),
            country_main=as_set(mi.country_main),
            country_main_id=as_set(mi.country_main_id),
            industrysector=as_set(mi.industrysector),
            industrysector_id=as_set(mi.industrysector_id),
            keyword=as_set(mi.keyword),
            keyword_id=as_set(mi.keyword_id),
            malwarekit=as_set(mi.malwarekit),
            malwarekit_id=as_set(mi.malwarekit_id),
            provider=as_set(mi.provider),
            provider_id=as_set(mi.provider_id),
            source=as_set(mi.source),
            source_id=as_set(mi.source_id),
            technology=as_set(mi.technology),
            technology_id=as_set(mi.technology_id),
            threatactor=as_set(mi.threatactor),
            threatactor_id=as_set(mi.threatactor_id),
            vulnerability=as_set(mi.vulnerability),
            vulnerability_id=as_set(mi.vulnerability_id),
        )
        if mi
        else NewSectionCatalog(),
        common=NewSectionCommon(),
        data=NewSectionData(
            raw=data_raw,
            structured=msg.source.document or {},
        ),
        entities=NewSectionEntities(
            cve=as_set(msg.source.attributes.cve) if msg.source.attributes else None,
            author=as_set(msg.source.common.author) if msg.source.common else None,
        ),
        metadata=NewSignalMetadata(
            id=signal_id,
            link=msg.source.metadata.doc_id if msg.source.metadata else None,
            published_at=msg.source.metadata.observation_time
            if msg.source.metadata
            else None,
            ingested_at=msg.source.system.first_seen if msg.source.system else None,
            updated_at=msg.source.system.first_seen if msg.source.system else None,
            version=0,
        ),
        system=NewSystem(
            ttl=msg.source.system.ttl,
            previous=as_list(msg.source.system.src_chain),
            source=msg.source.metadata.source if msg.source.metadata else index,
        ),
    )

    # metadata link
    if index == "dnslookup":
        host = None
        if sig.attributes.hostname:
            host = sig.attributes.hostname[0]
        elif "hostname" in sig.data.structured:
            if isinstance(sig.data.structured["hostname"], list):
                host = sig.data.structured["hostname"][0]
            elif isinstance(sig.data.structured["hostname"], str):
                host = sig.data.structured["hostname"]

        if host:
            sig.metadata.link = f"dns://{host}"
            sig.common.title = f"DNS {host}"
    elif index == "certstream":
        if (
            "CTLog" in sig.data.structured
            and "fingerprint_sha256" in sig.data.structured
        ):
            fp = sig.data.structured["fingerprint_sha256"]
            if (
                "subject" in sig.data.structured
                and "common_name" in sig.data.structured["subject"]
            ):
                cn = sig.data.structured["subject"]["common_name"]
                sig.common.title = f"Certificate {cn} ({fp})"
            else:
                sig.common.title = "certstream"

            sig.metadata.link = f"ct://{sig.data.structured['CTLog']}/{fp}"
    elif index == "vti":
        if (
            "attributes" in sig.data.structured
            and "sha256" in sig.data.structured["attributes"]
        ):
            h = sig.data.structured["attributes"]["sha256"]
            sig.metadata.link = f"https://www.virustotal.com/gui/file/{h}"

            if (
                "context_attributes" in sig.data.structured
                and "rule_name" in sig.data.structured["context_attributes"]
            ):
                rn = sig.data.structured['context_attributes']['rule_name']
                sig.common.title = f"VirusTotal {h} ({rn})"

    return NewDocument(
        _index=msg.index,
        _type=msg.type_,
        _id=signal_id,
        _source=sig,
        _version=msg.version,
    )


rate_limit = 1000

with open("/home/quoint/ratelimit.txt") as f:
    try:
        v = f.readline()
        rate_limit = int(v.strip())
        print(f"rate limit set to {rate_limit}")
    except Exception:
        print(f"using default rate limit of {rate_limit}")

work_queue = asyncio.Queue(50)

QUOLLECTOR_HOST = os.getenv(
    "QUOLLECTOR_HOST",
    "search-prod-quollector-xfflw67fqkto6kuy2u4bd3r4gm.eu-central-1.es.amazonaws.com",
)
BULK_SIZE_THRESHOLD = 1024 * 1024


parser = argparse.ArgumentParser(
    prog="msg2msg",
    description="Convert old to new datamodel types in ES/OS",
    epilog="bottom text",
)

parser.add_argument("index")

parser.add_argument("-c", "--compress", action="store_true")
parser.add_argument("-t", "--from-ts")
parser.add_argument("-d", "--total-docs")
parser.add_argument("-b", "--batch-size", default=10000, type=int)

args = parser.parse_args()


client = httpx.AsyncClient(
    auth=(os.getenv("ES_USER", "ele"), "6MAQv$Tf&r59%9rwi!pZLe*Rvm9sTk4y"),
    timeout=httpx.Timeout(60.0),
    transport=httpx.AsyncHTTPTransport(
        retries=3,
        # cert=(
        #    os.getenv("ES_CERT", "/home/quoint/crt.pem"),
        #    os.getenv("ES_KEY", "/home/quoint/key.pem"),
        # ),
        # verify=os.getenv("ES_CA", "/home/quoint/QuointRootCA.crt"),
    ),
)


async def rate_limit_task():
    global rate_limit

    with Inotify() as inotify:
        inotify.add_watch("/home/quoint/ratelimit.txt", Mask.MODIFY)
        async for event in inotify:
            with open("/home/quoint/ratelimit.txt") as f:
                try:
                    v = f.readline()
                    rate_limit = int(v.strip())
                except Exception as e:
                    print(
                        f"could not update rate limit, current value is {rate_limit}: {e}\n\tline: {v}"
                    )


@retry(
    reraise=True,
    stop=stop_after_attempt(3),
)
async def index_file(
    index: str, filename: str, total_documents: int, last_timestamp: str | None
):
    global rate_limit
    prev_rate_limit = rate_limit

    rt = asyncio.create_task(rate_limit_task())

    _last_timestamp = last_timestamp

    tasks = []
    for _ in range(20):
        task = asyncio.create_task(bulk_index_batch(work_queue))
        tasks.append(task)

    if filename:
        if filename.endswith("zst"):
            in_file = zstandard.open(filename, mode="r", encoding="utf-8")
        else:
            in_file = open(filename, mode="r", encoding="utf-8")
    else:
        in_file = zstandard.open(f"{index}.jsonl.zst", mode="r", encoding="utf-8")

    if "-" in index:
        index_simple = index.rpartition("-")[0]
    else:
        index_simple = index.partition(".")[0]

    with tqdm(
        total=total_documents,
        unit="doc",
        desc=index,
        leave=True,
    ) as pb:
        of = io.StringIO()
        line_count = 0

        while line := in_file.readline():
            try:
                od = OldDocument.model_validate_json(line)
                nd = convert_doc(od, index=index_simple)
                # if last_timestamp and nd.source.timestamp < last_timestamp:
                #    continue

                of.write('{"index": {"_id": "' + nd.source.metadata.id + '"}}\n')
                of.write(
                    nd.source.model_dump_json(
                        by_alias=True, exclude_unset=True, exclude_none=True
                    )
                )
                of.write("\n")

                line_count += 1

                if of.tell() >= BULK_SIZE_THRESHOLD or line_count >= rate_limit:
                    await work_queue.put((of.getvalue().encode(), index))
                    of = io.StringIO()

                    if line_count >= rate_limit:
                        line_count = 0
                        # just sleep for 1s for rate limit purposes for now
                        # while it's not technically accurate, this is good enough for our purposes
                        await asyncio.sleep(1.0)

                        if prev_rate_limit != rate_limit:
                            pb.write(
                                f"rate limit changed from {prev_rate_limit} to {rate_limit}"
                            )
                            prev_rate_limit = rate_limit

                _last_timestamp = nd.source.timestamp
            except Exception as e:
                # write a log because the console is shared
                with open(f"{index}.log", "a") as lf:
                    lf.write(line + "\n" + str(e))

                raise e

            pb.update(1)

    in_file.close()

    buf = of.getvalue().encode()
    await work_queue.put((buf, index))
    await work_queue.join()

    for task in tasks:
        task.cancel()

    rt.cancel()
    # Wait until all worker tasks are cancelled.
    await asyncio.gather(*tasks, return_exceptions=True)


async def bulk_index_batch(queue: asyncio.Queue):
    headers = {
        "Content-Type": "application/x-ndjson",
        "Accept-Encoding": "gzip",
    }

    if args.compress:
        headers["Content-Encoding"] = "gzip"

    while True:
        v = await queue.get()

        try:
            buf = gzip.compress(v[0], 3) if args.compress else v[0]
            await _post_doc_batch(headers, v, buf)
        except Exception as e:
            print(e)
            sys.exit(1)

        queue.task_done()


@retry(
    reraise=True,
    wait=wait_exponential(multiplier=1, min=5, max=60),
    stop=stop_after_attempt(10),
)
async def _post_doc_batch(headers, v, buf):
    r = await client.post(
        f"https://{QUOLLECTOR_HOST}/{v[1]}/_bulk",
        data=buf,
        headers=headers,
    )

    if r.status_code == 429:
        raise Exception("too many requests")

    if r.status_code > 210:
        print(f"status: {r.status_code}, text: {r.text}")
    rv = r.json()

    if rv["errors"]:
        raise Exception(rv)

    return r


async def two_step(
    index: str, filename: str, last_timestamp: str | None, total_docs: int | None
):
    total_documents = total_docs or 0
    r = await client.get(f"https://{QUOLLECTOR_HOST}/_cat/indices?format=json")
    for v in r.json():
        if v["index"] == index:
            total_documents = int(v["docs.count"])

    if not os.path.exists(filename):
        print(f"{filename} does not exist, aborting")
        sys.exit(2)

    print(f"deleting index {index}")
    r = await client.delete(f"https://{QUOLLECTOR_HOST}/{index}")
    if r.status_code > 210:
        v = r.json()
        reason = v["error"]["reason"] if "reason" in v["error"] else v["error"]
        print(f"result: {reason}")
        sys.exit(1)
    else:
        print("success")

    print("waiting 5s for changes to propagate...")
    await asyncio.sleep(5)

    with open("mappings.json") as f:
        mappings = json.load(f)

    print(f"re-creating index {index}")
    r = await client.put(f"https://{QUOLLECTOR_HOST}/{index}", json=mappings)
    if r.status_code > 210:
        v = r.json()
        reason = v["error"]["reason"] if "reason" in v["error"] else v["error"]
        print(f"result: {reason}")
        sys.exit(1)
    else:
        print("success")

    await index_file(index, filename, total_documents, last_timestamp)

    os.remove(filename)


async def main():
    index_name = (
        os.path.basename(args.index)
        .replace(".jsonl", "")
        .replace(".zst", "")
        .replace(".json", "")
    )

    await two_step(
        index_name,
        args.index,
        args.from_ts,
        int(args.total_docs) if args.total_docs else None,
    )


asyncio.run(main())

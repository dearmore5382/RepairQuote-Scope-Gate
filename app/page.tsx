'use client';
/* oxlint-disable next/no-html-link-for-pages -- Native navigation is intentional: client-side Link routing did not navigate in the deployed Vinext Worker. */
import Image from 'next/image';
import { useEffect, useState, type FormEvent } from 'react';
import { abi, createClient } from 'genlayer-js';
import { studionet } from 'genlayer-js/chains';
import { TransactionHashVariant } from 'genlayer-js/types';
import {
  Archive,
  ArrowRight,
  CheckCircle2,
  FileJson,
  Link2,
  LockKeyhole,
  RefreshCw,
  ScanSearch,
  ShieldCheck,
  Wallet,
  ListFilter,
  UserRound,
} from 'lucide-react';
import deployment from './deployment.json';
import {
  addressOK,
  digestOK,
  hashOK,
  loadJournal,
  parseReview,
  stageOf,
  uint,
  verifyReadback,
} from './protocol.mjs';
type Provider = NonNullable<Parameters<typeof createClient>[0]>['provider'];
type Journal = {
  hash: string;
  sender: string;
  contract: string;
  args: string[];
  method: string;
  chainId: number;
  stage: string;
  detail: string;
  createdAt: string;
};
type ModelContext = {
  registerTool: (
    tool: {
      name: string;
      title: string;
      description: string;
      inputSchema: object;
      annotations: object;
      execute: (input: unknown) => unknown;
    },
    options?: { signal?: AbortSignal },
  ) => void | Promise<void>;
};
const address = deployment.contractAddress as `0x${string}`;
const configured =
  addressOK(address) && /^[a-f0-9]{64}$/.test(deployment.sourceSha256);
const writesEnabled = configured && deployment.liveAuditVerified;
const reader = createClient({ chain: studionet });
const short = (v: string) =>
  v.length > 14 ? `${v.slice(0, 7)}…${v.slice(-5)}` : v;
const message = (e: unknown) =>
  e instanceof Error ? e.message : 'The operation could not be completed.';
const same = (a: unknown, b: unknown) =>
  typeof a === 'string' &&
  typeof b === 'string' &&
  a.toLowerCase() === b.toLowerCase();
const decode = (value: unknown) => {
  if (
    !value ||
    typeof value !== 'object' ||
    !('raw' in value) ||
    !Array.isArray(value.raw)
  )
    throw new Error('Receipt calldata is unavailable.');
  return abi.calldata.decode(new Uint8Array(value.raw));
};

export default function HomePage() {
  const [route, setRoute] = useState('/');
  const [wallet, setWallet] = useState('');
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState(
    configured
      ? 'Read access is ready.'
      : 'Preview mode — deploy the reviewed contract to enable live actions.',
  );
  const [reviewId, setReviewId] = useState('0');
  const [review, setReview] = useState<ReturnType<typeof parseReview> | null>(
    null,
  );
  const [journal, setJournal] = useState<Journal[]>([]);
  const [reviews, setReviews] = useState<
    (ReturnType<typeof parseReview> & { id: number })[]
  >([]);
  useEffect(() => setRoute(window.location.pathname), []);
  useEffect(() => {
    try {
      setJournal(loadJournal(localStorage.getItem('repairquote:journal:v1')));
    } catch (e) {
      setNotice(message(e));
    }
  }, []);
  useEffect(() => {
    const context = (document as Document & { modelContext?: ModelContext })
      .modelContext;
    if (!context?.registerTool) return;
    const lifecycle = new AbortController();
    void Promise.resolve(
      context.registerTool(
        {
          name: 'stage_quote_review',
          title: 'Stage quote review',
          description:
            'Set the visible RepairQuote Scope Gate review ID without reading chain state or sending a transaction.',
          inputSchema: {
            type: 'object',
            properties: {
              reviewId: { type: 'string', pattern: '^(0|[1-9][0-9]*)$' },
            },
            required: ['reviewId'],
            additionalProperties: false,
          },
          annotations: { readOnlyHint: false, untrustedContentHint: false },
          execute(input) {
            if (!input || typeof input !== 'object')
              throw new Error('Invalid review ID.');
            const value = String((input as { reviewId?: unknown }).reviewId);
            uint(value);
            setReviewId(value);
            setNotice(
              'Review ID staged. Use Read to load authoritative state.',
            );
            return { reviewId: value, status: 'staged' };
          },
        },
        { signal: lifecycle.signal },
      ),
    ).catch(() => undefined);
    return () => lifecycle.abort();
  }, []);
  const save = (rows: Journal[]) => {
    localStorage.setItem('repairquote:journal:v1', JSON.stringify(rows));
    setJournal(rows);
  };
  async function connect() {
    setBusy(true);
    try {
      if (!writesEnabled)
        throw new Error(
          'Writes unlock after deployment and live verification.',
        );
      const provider = (window as unknown as { ethereum?: Provider }).ethereum;
      if (!provider) throw new Error('Install an EIP-1193 browser wallet.');
      const accounts = (await provider.request({
        method: 'eth_requestAccounts',
      })) as string[];
      if (!addressOK(accounts[0]))
        throw new Error('No valid account selected.');
      await provider.request({
        method: 'wallet_switchEthereumChain',
        params: [{ chainId: `0x${studionet.id.toString(16)}` }],
      });
      setWallet(accounts[0]);
      setNotice('Wallet connected on Studionet.');
    } catch (e) {
      setNotice(message(e));
    } finally {
      setBusy(false);
    }
  }
  async function read(id = reviewId) {
    if (!configured)
      throw new Error('Deploy and configure the reviewed contract first.');
    const raw = await reader.readContract({
      address,
      functionName: 'get_review',
      args: [uint(id)],
      transactionHashVariant: TransactionHashVariant.LATEST_FINAL,
    });
    const value = parseReview(raw);
    setReview(value);
    setReviewId(id);
    return value;
  }
  async function refresh() {
    setBusy(true);
    try {
      await read();
      setNotice('Loaded finalized review state.');
    } catch (e) {
      setNotice(message(e));
    } finally {
      setBusy(false);
    }
  }
  async function loadExplorer() {
    setBusy(true);
    try {
      const countRaw = await reader.readContract({
        address,
        functionName: 'get_review_count',
        args: [],
        transactionHashVariant: TransactionHashVariant.LATEST_FINAL,
      });
      const count = Math.min(Number(String(countRaw)), 100);
      const rows = await Promise.all(
        Array.from({ length: count }, async (_, id) => {
          const raw = await reader.readContract({
            address,
            functionName: 'get_review',
            args: [BigInt(id)],
            transactionHashVariant: TransactionHashVariant.LATEST_FINAL,
          });
          return { ...parseReview(raw), id };
        }),
      );
      setReviews(rows.reverse());
      setNotice(`Loaded ${rows.length} finalized review records.`);
    } catch (e) {
      setNotice(message(e));
    } finally {
      setBusy(false);
    }
  }
  async function send(method: string, args: (string | bigint)[]) {
    setBusy(true);
    try {
      if (!writesEnabled || !wallet)
        throw new Error('Connect a verified Studionet wallet before writing.');
      if (
        localStorage.getItem('repairquote:intent:v1') ||
        journal.some((r) => !['VERIFIED', 'FAILED'].includes(r.stage))
      )
        throw new Error(
          'Reconcile the existing transaction before sending another.',
        );
      const provider = (window as unknown as { ethereum?: Provider }).ethereum;
      if (!provider) throw new Error('Wallet disconnected.');
      const intent = {
        method,
        args: args.map(String),
        sender: wallet,
        contract: address,
        chainId: studionet.id,
        createdAt: new Date().toISOString(),
      };
      localStorage.setItem('repairquote:intent:v1', JSON.stringify(intent));
      const writer = createClient({
        chain: studionet,
        account: wallet as `0x${string}`,
        provider,
      });
      let hash: unknown;
      try {
        hash = await writer.writeContract({
          address,
          functionName: method,
          args,
          value: 0n,
          leaderOnly: false,
        });
      } catch (e) {
        if (typeof e === 'object' && e && 'code' in e && e.code === 4001)
          localStorage.removeItem('repairquote:intent:v1');
        throw e;
      }
      if (!hashOK(hash))
        throw new Error(
          'Invalid transaction hash. Preserve the intent and do not resubmit.',
        );
      const row: Journal = {
        ...intent,
        hash: String(hash),
        stage: 'PENDING',
        detail: 'Submitted once; awaiting finality.',
      };
      save([...journal, row]);
      localStorage.removeItem('repairquote:intent:v1');
      setNotice(
        `Submitted ${short(row.hash)}. Recheck this hash; do not resubmit.`,
      );
    } catch (e) {
      setNotice(message(e));
    } finally {
      setBusy(false);
    }
  }
  function runLifecycleAction(
    method: 'capture_sources' | 'assess_quote' | 'close_review',
    requiredStatus: 'DRAFT' | 'CAPTURED' | 'ASSESSED',
  ) {
    if (!wallet) {
      setNotice('Connect a Studionet wallet first, then retry this action.');
      void connect();
      return;
    }
    if (!review) {
      setNotice('Enter a review ID and click Read before choosing a lifecycle action.');
      return;
    }
    if (review.status !== requiredStatus) {
      setNotice(
        `This action requires ${requiredStatus}; review ${reviewId} is ${review.status}.`,
      );
      return;
    }
    if (method === 'close_review' && !same(wallet, review.creator)) {
      setNotice('Only the creator wallet shown in this review may close it.');
      return;
    }
    void send(method, [uint(reviewId)]);
  }
  async function reconcile(row: Journal) {
    setBusy(true);
    try {
      const tx = await reader.getTransaction({
        hash: row.hash as Parameters<typeof reader.getTransaction>[0]['hash'],
      });
      const state = stageOf(tx);
      let updated = { ...row, ...state };
      if (state.stage === 'READBACK_REQUIRED') {
        const t = tx as unknown as {
          hash?: string;
          txId?: string;
          from_address?: string;
          sender?: string;
          to_address?: string;
          recipient?: string;
          data?: { calldata?: unknown };
          consensus_data?: { leader_receipt?: unknown | unknown[] };
        };
        if (
          !same(t.hash ?? t.txId, row.hash) ||
          !same(t.from_address ?? t.sender, row.sender) ||
          !same(t.to_address ?? t.recipient, row.contract)
        )
          throw new Error('Receipt identity does not match the journal.');
        const receipts = t.consensus_data?.leader_receipt;
        const leader = (
          Array.isArray(receipts) ? receipts.at(-1) : receipts
        ) as { calldata?: unknown; result?: { payload?: unknown } } | undefined;
        const call = decode(t.data?.calldata ?? leader?.calldata);
        const result = decode(leader?.result?.payload);
        if (
          !(call instanceof Map) ||
          call.get('method') !== row.method ||
          JSON.stringify((call.get('args') as unknown[]).map(String)) !==
            JSON.stringify(row.args)
        )
          throw new Error(
            'Finalized method or arguments do not match the journal.',
          );
        const returned = String(result);
        const id = row.method === 'create_review' ? returned : row.args[0];
        uint(id);
        const current = await read(id);
        verifyReadback(row, returned, current);
        if (row.method === 'create_review') setReviewId(id);
        updated = {
          ...updated,
          stage: 'VERIFIED',
          detail:
            'Finalized, consensus agreed, and authoritative readback verified.',
        };
      }
      save(journal.map((v) => (v.hash === row.hash ? updated : v)));
      setNotice(updated.detail);
    } catch (e) {
      setNotice(message(e));
    } finally {
      setBusy(false);
    }
  }
  function create(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const d = new FormData(e.currentTarget);
    const values = [
      'title',
      'approvedUrl',
      'approvedHash',
      'quoteUrl',
      'quoteHash',
    ].map((k) => String(d.get(k)).trim());
    if (!digestOK(values[2]) || !digestOK(values[4])) {
      setNotice(
        'Each SHA-256 digest must contain exactly 64 hexadecimal characters.',
      );
      return;
    }
    void send('create_review', values);
  }
  const badge =
    review?.verdict === 'QUOTE_ACCEPTABLE'
      ? 'pass'
      : review?.verdict === 'SCOPE_VIOLATION'
        ? 'fail'
        : 'review';
  return (
    <main className={`app-shell route-${route.replace('/', '') || 'home'}`}>
      <header className="topbar">
        <a className="brand" href="#workspace">
          <Image
            src="/repairquote-logo.png"
            alt="RepairQuote Scope Gate mark"
            width={46}
            height={46}
          />
          <span>
            RepairQuote <b>Scope Gate</b>
          </span>
        </a>
        <nav className="main-nav" aria-label="Primary navigation">
          <a href="/" aria-current={route === '/' ? 'page' : undefined}>Overview</a>
          <a href="/create" aria-current={route === '/create' ? 'page' : undefined}>New review</a>
          <a href="/explorer" aria-current={route === '/explorer' ? 'page' : undefined}>Explorer</a>
        </nav>
        <div className="contract-chip">
          <i /> Studionet · {configured ? short(address) : 'pre-deployment'}
        </div>
        <button
          className="wallet-button"
          onClick={connect}
          disabled={busy}
        >
          <Wallet size={17} />
          {wallet ? short(wallet) : 'Connect wallet'}
        </button>
      </header>
      <section className="intro" id="workspace">
        <div>
          <span className="eyebrow">
            AUTHENTICATED QUOTE REVIEW · NON-PAYABLE
          </span>
          <h1>
            Bind the source.
            <br />
            <em>Gate the scope.</em>
          </h1>
          <p>
            Compare a commercial repair quote against an immutable approved
            scope. Exact bytes and SHA-256 bindings come first; AI is limited to
            one narrow scope verdict.
          </p>
          <div className="hero-actions">
            <a href="/create">Create a review <ArrowRight size={17} /></a>
            <a href="/explorer" className="secondary">Browse completed cases</a>
          </div>
        </div>
        <div className="process-map">
          {[
            ['01', 'Register', 'Pin URLs + digests'],
            ['02', 'Capture', 'Verify exact bytes'],
            ['03', 'Assess', 'Classify scope fit'],
            ['04', 'Close', 'Freeze the result'],
          ].map((x) => (
            <div key={x[0]}>
              <span>{x[0]}</span>
              <b>{x[1]}</b>
              <small>{x[2]}</small>
            </div>
          ))}
        </div>
        {route === '/' && (
          <section className="home-explainer" aria-labelledby="how-title">
            <div className="explainer-heading">
              <span className="eyebrow">HOW IT WORKS · FAQ</span>
              <h2 id="how-title">Clear inputs. Narrow decision.</h2>
              <p>Every result can be traced back to exact public bytes and an authoritative on-chain record.</p>
            </div>
            <div className="faq-list">
              <details open>
                <summary>Where does the evidence come from?</summary>
                <p>The creator locks commit-pinned raw JSON URLs and their SHA-256 digests. Validators fetch those exact URLs and recompute both hashes before any assessment.</p>
              </details>
              <details>
                <summary>Who can run each step?</summary>
                <p>Any connected wallet may capture and assess the locked public package. Only the review creator can close an assessed record.</p>
              </details>
              <details>
                <summary>What does the AI decide?</summary>
                <p>Only whether quoted work fits the authenticated approved scope: acceptable, scope violation, or review required. It does not decide price, liability, quality, or payment.</p>
              </details>
            </div>
          </section>
        )}
      </section>
      {route === '/explorer' && (
        <section className="explorer-page" id="workspace">
          <div className="explorer-head">
            <div>
              <span className="eyebrow">PUBLIC REVIEW EXPLORER</span>
              <h1>Finalized records, readable by anyone.</h1>
              <p>Load authoritative StudioNet state, select a record, and see exactly which action is valid next.</p>
            </div>
            <button onClick={() => void loadExplorer()} disabled={busy}>
              <ListFilter /> Load all records
            </button>
          </div>
          <div className="review-grid">
            {reviews.map((item) => (
              <button key={item.id} className="review-card" onClick={() => void read(String(item.id))}>
                <span>REVIEW {String(item.id).padStart(3, '0')}</span>
                <h3>{item.title}</h3>
                <p>{item.status} · {item.verdict.replaceAll('_', ' ')}</p>
                <small>{short(item.creator)}</small>
              </button>
            ))}
            {!reviews.length && <div className="empty-records">Select “Load all records” to read completed and in-progress cases from StudioNet.</div>}
          </div>
        </section>
      )}
      <section className="desk">
        <aside className="case-rail">
          <span className="section-label">REVIEW RECORD</span>
          <h2>{review?.title ?? 'No review loaded'}</h2>
          <p>Record {reviewId}</p>
          <div className="rail-state">
            <FileJson />
            <div>
              <b>Source package</b>
              <span>{review?.status ?? 'Not loaded'}</span>
            </div>
          </div>
          <div className="rail-state">
            <ScanSearch />
            <div>
              <b>Scope verdict</b>
              <span>{review?.verdict ?? 'UNASSESSED'}</span>
            </div>
          </div>
          <div className="boundary">
            <ShieldCheck />
            <div>
              <b>Decision boundary</b>
              <p>
                Checks scope alignment only. It does not judge price,
                workmanship, urgency, liability, or payment.
              </p>
            </div>
          </div>
        </aside>
        <div className="work-canvas">
          <div className="canvas-head">
            <div>
              <span className="section-label">SOURCE BINDER</span>
              <h2>Register an immutable review package</h2>
            </div>
            <span className="step-status">
              <LockKeyhole />{' '}
              {writesEnabled
                ? 'Verified deployment'
                : 'Writes locked until verified deployment'}
            </span>
          </div>
          <div className="role-callout">
            <UserRound />
            <div><b>Who may do what?</b><span>Anyone may capture and assess locked sources. Only the review creator may close an assessed record.</span></div>
          </div>
          <form className="source-binder-form" onSubmit={create}>
            <label className="wide">
              Review title
              <input
                name="title"
                defaultValue="Kitchen sink quote — RQS-204"
                maxLength={160}
                required
              />
            </label>
            <label>
              Approved scope URL
              <input
                name="approvedUrl"
                type="url"
                placeholder="https://raw.githubusercontent.com/…/scope.json"
                required
              />
            </label>
            <label>
              Approved scope SHA-256
              <input
                name="approvedHash"
                pattern="[0-9a-fA-F]{64}"
                placeholder="64 hexadecimal characters"
                required
              />
            </label>
            <label>
              Contractor quote URL
              <input
                name="quoteUrl"
                type="url"
                placeholder="https://raw.githubusercontent.com/…/quote.json"
                required
              />
            </label>
            <label>
              Contractor quote SHA-256
              <input
                name="quoteHash"
                pattern="[0-9a-fA-F]{64}"
                placeholder="64 hexadecimal characters"
                required
              />
            </label>
            <button
              className="primary-action"
              disabled={busy}
            >
              Create review <ArrowRight size={17} />
            </button>
          </form>
          <div className="action-strip">
            <label>
              Review ID
              <input
                value={reviewId}
                onChange={(e) => setReviewId(e.target.value)}
                inputMode="numeric"
              />
            </label>
            <button
              onClick={() => void refresh()}
              disabled={busy}
            >
              <RefreshCw /> Read
            </button>
            <button
              onClick={() => runLifecycleAction('capture_sources', 'DRAFT')}
              disabled={busy}
            >
              <Link2 /> Capture
            </button>
            <button
              onClick={() => runLifecycleAction('assess_quote', 'CAPTURED')}
              disabled={busy}
            >
              <ScanSearch /> Assess
            </button>
            <button
              onClick={() => runLifecycleAction('close_review', 'ASSESSED')}
              disabled={busy}
              title="Only the review creator may complete this terminal transition."
            >
              <Archive /> Close
            </button>
          </div>
          <output className="action-feedback">{notice}</output>
          {review && (
            <div className="next-action">
              <b>Next valid action</b>
              <span>{review.status === 'DRAFT' ? 'Capture sources — available to any connected wallet.' : review.status === 'CAPTURED' ? 'Run assessment — available to any connected wallet.' : review.status === 'ASSESSED' ? (same(wallet, review.creator) ? 'Close review — you are connected as creator.' : 'Only the creator can close. This wallet may still inspect the finalized assessment.') : 'This record is closed and read-only.'}</span>
            </div>
          )}
          <div className="source-board">
            <article>
              <span>APPROVED SCOPE</span>
              <b>
                {review ? short(review.approvedSha256) : 'Digest not loaded'}
              </b>
              <small>
                {review?.approvedUrl ?? 'Commit-pinned raw JSON URL'}
              </small>
            </article>
            <ArrowRight />
            <article>
              <span>CONTRACTOR QUOTE</span>
              <b>{review ? short(review.quoteSha256) : 'Digest not loaded'}</b>
              <small>{review?.quoteUrl ?? 'Commit-pinned raw JSON URL'}</small>
            </article>
          </div>
        </div>
      </section>
      <section className={`decision-panel ${badge}`}>
        <div>
          <span className="section-label">AUTHORITATIVE VERDICT</span>
          <h2>{review?.verdict ?? 'Awaiting assessment'}</h2>
          <p>
            {review?.reason
              ? review.reason.replaceAll('_', ' ').toLowerCase()
              : 'A verdict appears only after exact source capture, digest verification, finality, consensus, and contract readback.'}
          </p>
        </div>
        <div className="decision-facts">
          <div>
            <CheckCircle2 />
            <span>Review state</span>
            <b>{review?.status ?? 'Not loaded'}</b>
          </div>
          <div>
            <ShieldCheck />
            <span>Source binding</span>
            <b>
              {review && review.status !== 'DRAFT' ? 'Captured' : 'Pending'}
            </b>
          </div>
          <div>
            <ScanSearch />
            <span>Scope result</span>
            <b>{review?.verdict ?? 'UNASSESSED'}</b>
          </div>
        </div>
      </section>
      <section className="journal-panel">
        <div>
          <span className="section-label">TRANSACTION JOURNAL</span>
          <h2>One intent. One hash.</h2>
        </div>
        <output>{notice}</output>
        {journal.length ? (
          journal.map((row) => (
            <article key={row.hash}>
              <span>
                <RefreshCw />
              </span>
              <div>
                <b>{row.method}</b>
                <small>
                  {short(row.hash)} · {row.stage}
                </small>
              </div>
              <button
                onClick={() => void reconcile(row)}
                disabled={busy || row.stage === 'VERIFIED'}
              >
                Recheck
              </button>
            </article>
          ))
        ) : (
          <p>
            No browser transactions yet. Pending hashes persist across
            refreshes.
          </p>
        )}
      </section>
      <footer>
        <div className="brand small">
          <Image src="/repairquote-logo.png" alt="" width={38} height={38} />
          <span>
            RepairQuote <b>Scope Gate</b>
          </span>
        </div>
        <p>Authenticated scope review for commercial repair quotes.</p>
        <span>Built on GenLayer Studionet</span>
      </footer>
    </main>
  );
}

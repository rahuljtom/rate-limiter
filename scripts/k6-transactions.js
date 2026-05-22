import http from 'k6/http';
import { check } from 'k6';
import { Counter } from 'k6/metrics';

const rateLimited = new Counter('rate_limited_responses');
const successful = new Counter('successful_responses');

const BASE_URL = __ENV.BASE_URL || 'http://127.0.0.1:8000';
const TOKEN = __ENV.TOKEN;

if (!TOKEN) {
  throw new Error('Set TOKEN env var (JWT from POST /auth/login)');
}

export const options = {
  vus: 100,
  duration: '1m',
};

export default function () {
  const idempotencyKey = `k6-${__VU}-${__ITER}-${Date.now()}`;
  const res = http.post(`${BASE_URL}/transactions`, null, {
    headers: {
      Authorization: `Bearer ${TOKEN}`,
      'Idempotency-Key': idempotencyKey,
    },
  });

  if (res.status === 429) {
    rateLimited.add(1);
  } else if (res.status === 200) {
    successful.add(1);
  }

  check(res, {
    '200 or 429': (r) => r.status === 200 || r.status === 429,
  });
}

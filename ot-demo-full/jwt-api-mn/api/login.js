const jwt = require("jsonwebtoken");
const crypto = require("crypto");

function safeEqual(a, b) {
  const x = Buffer.from(String(a));
  const y = Buffer.from(String(b));
  return x.length === y.length && crypto.timingSafeEqual(x, y);
}

module.exports = async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
  res.setHeader("Cache-Control", "no-store");
  if (req.method === "OPTIONS") return res.status(204).end();
  if (req.method !== "POST") return res.status(405).json({ error: "Method not allowed" });

  const configuredEmail = String(process.env.DEMO_USER_EMAIL || "").trim().toLowerCase();
  const configuredCode = String(process.env.DEMO_ACCESS_CODE || "");
  const privateKeyB64 = String(process.env.JWT_PRIVATE_KEY_B64 || "");
  const keyId = String(process.env.JWT_KEY_ID || "").trim();
  if (!configuredEmail || !configuredCode || !privateKeyB64 || !keyId) {
    return res.status(500).json({ error: "Server configuration is incomplete" });
  }

  const email = String(req.body?.email || "").trim().toLowerCase();
  const accessCode = String(req.body?.accessCode || "");
  if (!safeEqual(email, configuredEmail) || !safeEqual(accessCode, configuredCode)) {
    return res.status(401).json({ error: "Invalid email or access code" });
  }

  try {
    const privateKey = Buffer.from(privateKeyB64, "base64").toString("utf8");
    const token = jwt.sign({ sub: email }, privateKey, {
      algorithm: "RS256",
      expiresIn: "15m",
      keyid: keyId
    });
    return res.status(200).json({ userId: email, token });
  } catch (error) {
    console.error("JWT generation failed", error);
    return res.status(500).json({ error: "Could not create authentication token" });
  }
};

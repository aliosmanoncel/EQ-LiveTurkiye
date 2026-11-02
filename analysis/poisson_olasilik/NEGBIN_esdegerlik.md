# NegBin (Gamma–Poisson) örnekleyicisinin eski olay-başına örnekleyiciye eşdeğerliği

Aşama 3, 2026-11-01. Kod: `index.html` → `gammaSample`, `grBootDraws`, `grPoissonBootSimple`, `cmpProbBoot`. Sayısal doğrulama: `negbin_karsilastirma.js` (sonuç: `negbin_karsilastirma.json`), birim testi `scripts/test_cmp_prob.js` (i), kabul testi `kabul_cmp_prob.js` (8).

## 1. Soru

Eski örnekleyici (commit 1f28df9, `grPoissonBootSimple` ve `cmpProbBoot`) her bootstrap tekrarında n\* büyüklük çekiyordu. Toplam çekiliş 4·10⁶ ile sınırlıydı; bu yüzden Türkiye (n = 27 346) için B = 200'e düşüyordu. Yeni örnekleyici tekrar başına yalnız üç rastgele değişken çeker: n\*, bir gama ve bir Poisson.

Bu belgenin göstermek istediği: (n\*, b\*) ortak dağılımı ve dolayısıyla (a\*, b\*), λ\*(≥M), P\*(≥M; t) iki şemada **aynıdır**. İstatistiksel varsayımların hiçbiri değişmez; değişen yalnız rastgele sayı akışıdır.

## 2. Eski şema (tanım)

Gözlenen: n = N(≥Mc), b̂ (Aki–Utsu), Mc, ΔM, T. β̂ = b̂ ln 10. Her tekrar r = 1, …, B için:

1. n\* ~ Poisson(n). n\* < 10 ise tekrar reddedilir.
2. i = 1, …, n\* için:
   - Eᵢ ~ Exp(β̂) bağımsız çekilir.
   - Xᵢ = Mc − ΔM/2 + Eᵢ.
   - mᵢ = `bGridRound`(Xᵢ, Mc, ΔM) = Mc + ΔM·round((Xᵢ − Mc)/ΔM).
3. b\* = `computeBvalue` = log₁₀e / (m̄ − Mc + ΔM/2), Aki (1965), ΔM/2 düzeltmesi Utsu (1965).
4. a\* = log₁₀(n\*/T) + b\*·Mc. λ\*(≥M) = (n\*/T)·10^(−b\*(M − Mc)).

## 3. Lemmalar

**Lemma 1 (ızgara Mc'ye bağlı; yuvarlanmış büyüklük geometriktir).**
- Tanım gereği (Xᵢ − Mc)/ΔM = Eᵢ/ΔM − 1/2.
- JavaScript `Math.round(y)` = ⌊y + 1/2⌋ (ECMAScript: yarım değerler +∞ yönüne yuvarlanır). Bu nedenle round(Eᵢ/ΔM − 1/2) = ⌊Eᵢ/ΔM⌋ =: Kᵢ.
- Koddaki +10⁻⁹ kaydırması sınırı 10⁻⁹ birim oynatır. Etkisi olasılık ≤ 10⁻⁹ düzeyindedir. Kayan nokta hatası (~10⁻¹⁵) bunun da altındadır.
- Dolayısıyla mᵢ = Mc + ΔM·Kᵢ ve P(Kᵢ ≥ k) = P(Eᵢ ≥ kΔM) = e^(−β̂ΔM·k) = qᵏ, burada q = 10^(−b̂ΔM).
- Kᵢ ∈ {0, 1, …}, başarı olasılığı p = 1 − q olan geometrik dağılıma uyar ve Kᵢ'ler bağımsızdır.
- Her mᵢ ≥ Mc olduğundan `computeBvalue` n\*'ın tamamını kullanır. Payda ΔM·K̄ + ΔM/2 > 0 olduğundan b\* hiçbir zaman reddedilmez. Ret yalnız n\* < 10'dan gelir; bu yeni şemada da aynıdır.

**Lemma 2 (b\* yalnız (n\*, S)'ye bağlıdır).**
S = Σᵢ Kᵢ olsun. m̄ − Mc = ΔM·S/n\* olduğundan b\* = log₁₀e / (ΔM·S/n\* + ΔM/2). Aki–Utsu kestiricisi örneklem ortalamasının fonksiyonudur; S, geometrik model için yeterli istatistiktir. Tek tek büyüklüklere gerek yoktur.

**Lemma 3.** n\* verildiğinde S, n\* bağımsız geometrik değişkenin toplamıdır. Dolayısıyla S | n\* ~ NegBin(n\*, p):

P(S = s) = C(s + n\* − 1, s)·p^(n\*)·q^s.

**Lemma 4 (Gamma–Poisson karışımı).** G ~ Gamma(şekil n\*, ölçek θ = q/p) ve S | G ~ Poisson(G) ise S ~ NegBin(n\*, p). Kanıt:

P(S = s) = ∫₀^∞ e^(−g) g^s/s! · g^(n\*−1) e^(−g/θ) / (Γ(n\*) θ^(n\*)) dg = Γ(s + n\*) / (s! Γ(n\*)) · θ^s / (1 + θ)^(s + n\*).

θ/(1 + θ) = q ve 1/(1 + θ) = p olduğundan bu ifade Lemma 3'teki olasılıktır. ∎ (Johnson, Kemp ve Kotz 2005, §5.3.)

## 4. Teorem

Yeni şema (`grBootDraws`), her tekrarda:
- n\* ~ Poisson(n) çeker; n\* < 10 ise tekrarı reddeder (eski şemayla aynı);
- G ~ Gamma(n\*, 1)·q/(1 − q) ve S ~ Poisson(G) çeker;
- b\* = log₁₀e / (ΔM·S/n\* + ΔM/2) hesaplar.

Bu şema (n\*, S)'nin ortak dağılımını eski şemayla birebir aynı üretir:
- n\* marjinali aynıdır (Poisson(n), aynı ret kuralı);
- S | n\* aynıdır (Lemma 3 ve 4).

b\* = f(n\*, S) (Lemma 2) ve a\*, λ\*, P\* ise (n\*, b\*)'ın fonksiyonlarıdır. Bu nedenle bunların **ortak** dağılımları eşittir. Özellikle cov(a\*, b\*) yaklaşık olarak değil, **tam** olarak korunur. ∎

Kullanılan örnekleyiciler kesin (exact) ret algoritmalarıdır:
- Gamma: Marsaglia ve Tsang (2000), şekil ≥ 1 için kesin; burada n\* ≥ 10.
- Poisson: Knuth (μ < `GR_QC.poissonKnuthMax`) ve PTRS (Hörmann 1993). Bunlar eski şemada n\* için de kullanılan algoritmalardır.

Sayısal fark, eski şemadaki `toFixed(6)` yuvarlaması ve toplama sırası düzeyindedir (göreli ~10⁻¹⁵).

## 5. Multinomial ve bağımsız Poisson sorusu

İki farklı nesneyi ayırmak gerekir.

**(a) Sınıf sayıları.** C_k = #{i : Kᵢ = k}:
- n\* verildiğinde Multinomial(n\*; p·qᵏ) dağılır;
- n\* ~ Poisson(n) olduğunda ise Poisson inceltmesiyle bağımsız Poisson(n·p·qᵏ) olur.

Bu iki ifade çelişmez; aynı şemanın koşullu ve koşulsuz görünümleridir. Eski şema da yeni şema da tam olarak bu yapıyı taşır. Yeni şema sınıf sayılarını ayrı ayrı çekmez; aynı modelin yeterli istatistiği S'yi doğrudan çeker. b\* yalnız S'ye bağlı olduğundan sınıf sayılarının ayrıntısı sonucu değiştirmez.

**(b) Sabit N ile yerine koyarak (parametrik olmayan) bootstrap.** Gözlenen büyüklükler sabit n ile yeniden örneklenir; sayılar ampirik sınıf olasılıklarıyla multinomial olur ve a yalnız b üzerinden değişir. Bu **farklı** bir şemadır. Ne eski ne yeni kodda kullanılır. Bu değişiklikte şemalar arası geçiş yoktur.

## 6. Sayısal doğrulama (`negbin_karsilastirma.js`)

Eski şema 1f28df9'dan `git show` ile okunur. Betikteki çekiliş döngüsünün o commit'teki fonksiyonla birebir aynı sonucu verdiği ayrıca sınanır (denetim 1). Sonuçlar §8'dedir.

| Denetim | İçerik |
|---|---|
| (2) beş senaryo | Örnekler n = 50 (küçük N), n = 624 (Marmara), n = 5007 (Doğu Anadolu), n = 27 346 (Türkiye) ve ΔM = 0,2 ile b = 0,8. Her birinde b\* ve a\* için iki örneklem KS; a\*, b\*, λ\*(≥6) ve P\*(≥7; 50 yıl) için 2,5–97,5 yüzdelikleri; ortalama, varyans, cov ve corr(a\*, b\*), corr(n\*, b\*). Gürültü ölçeği, eski şemanın iki farklı tohumla kendisiyle farkıdır. |
| (3) S \| n\* | n\* ∈ {12, 30, 200}, 5 tohum × 40 000 örnek. Eski ve yeni şema, kesin NegBin olasılıklarına karşı χ² ile sınanır; p değerleri Fisher yöntemiyle birleştirilir. |
| (4) kapsama | 300 sentetik katalog (bilinen λ₀ ve b), B = 2000. Eski ve yeni %95 aralıklarının gerçek P(≥M; t)'yi kapsama oranı. |
| (5) süre | n = 27 346, B = 2000 için iki şemanın çalışma süresi. |

## 7. Değişmeyen ve değişen

- **Değişmeyen:** model (kesilmesiz G–R, tek Mc, Aki–Utsu), parametrik bootstrap varsayımları, ret kuralı, tohum (20261027), nokta kestirimleri (λ, P, Tr).
- **Değişen:**
  - Rastgele sayı akışı. Aynı tohumla aralık sınırları Monte Carlo gürültüsü kadar farklıdır; birebir eşitlik beklenmez.
  - B: tüm n'lerde 2000. Eski şemada büyük n'de 200'e düşüyordu; artış Monte Carlo gürültüsünü azaltır.
  - Sağlamlık denetimi URL'de `?bootB=5000` ile yapılır.
- **Ortak örnekleyici:** G–R paneli (`grPoissonBootSimple`), dönem raporu (aynı fonksiyon) ve bölge karşılaştırması (`cmpProbBoot`) aynı `grBootDraws` çekilişlerini kullanır (birim testi (i), kabul (8)).
- **Kapsam dışı (ayrı karar):** Weichert bootstrap'ı (`grPoissonBootWeichert`) sınıf başına Poisson çeker. Zaten O(K) maliyetlidir ve bu aşamada değiştirilmedi; B = 1000'de kaldı (`GR_POIS.Bw`).

## 8. Bulgular

Kaynaklar: `negbin_karsilastirma.json` ve `kabul_cmp_prob_sonuc.json`.

- Denetim (2): beş senaryonun hepsinde KS p > 0,01. Yeni–eski yüzdelik farkları eski–eski gürültüsü düzeyinde. corr(a\*, b\*) iki şemada aynı: Türkiye benzeri senaryoda 0,993 / 0,993, Marmara benzerinde 0,991 / 0,991.
- Denetim (3): eski ve yeni şemanın χ² p değerleri düzgün dağılıyor. Yeni şema n\* = 200 için 20 tohumla ayrıca sınandı: p'lerin düzgünlüğü için KS D = 0,164 (%5 kritik değer ≈ 0,294).
- Denetim (4): kapsama eski ve yeni şemada %93–94 düzeyinde; aralarındaki fark ≤ %1 (300 katalogda binom standart hatası ≈ %1,3).
- Denetim (5): eski şema 37 s, yeni şema 9 ms (n = 27 346, B = 2000).
- Kabul testi, üç gerçek bölge:
  - B = 2000 ile 5000 arasında %95 sınırlarının en büyük farkı 0,65 yüzde puan (Marmara M ≥ 7, t = 100 yıl).
  - Eski (Türkiye'de B = 200) ve yeni (B = 2000) aralıklar en çok 0,6 yüzde puan farklı. Nokta kestirimleri aynı.

**Önceden var olan, bu değişiklikle ilgisiz bir bulgu (karar için).** Gruplanmış (ΔM) büyüklüklerde Aki–Utsu kestiricisi hafif sapmalıdır: E[b\*] ≈ log₁₀e / (ΔM(q/(1 − q) + 1/2)) ≠ b (Bender 1983; Tinti ve Mulargia 1987; Marzocchi ve Sandri 2003).
- Türkiye benzeri senaryoda b = 1,14 iken bootstrap ortancası 1,134'tür. Sapma ≈ 0,006, yani ≈ 0,9 standart sapma.
- Bu yüzden büyük n'de yüzdelik aralığı nokta kestirimine göre kaymıştır. Örneğin Türkiye P(≥7; 10 yıl) = %36,6, aralık [34,9–42,1].
- Küçük n'de etkisi ihmal edilebilir: Marmara'da sapma ≈ 0,1 standart sapma.
- Bu durum eski şemada da aynıydı; burada değiştirilmedi. Çözüm seçenekleri ayrı onay gerektirir: Bender'in gruplanmış veri için kesin ML kestiricisi, ya da sapması düzeltilmiş parametrik bootstrap.

## Kaynaklar

- Aki, K. (1965). Maximum likelihood estimate of b in the formula log N = a − bM and its confidence limits. *Bull. Earthq. Res. Inst. Univ. Tokyo* 43, 237–239.
- Bender, B. (1983). Maximum likelihood estimation of b values for magnitude grouped data. *BSSA* 73(3), 831–851.
- Efron, B., Tibshirani, R. J. (1993). *An Introduction to the Bootstrap*. Chapman & Hall (parametrik bootstrap, §6.5).
- Hörmann, W. (1993). The transformed rejection method for generating Poisson random variables. *Insurance: Math. Econ.* 12, 39–45.
- Johnson, N. L., Kemp, A. W., Kotz, S. (2005). *Univariate Discrete Distributions*, 3. baskı. Wiley (negatif binom, Gamma–Poisson karışımı, §5.3).
- Marsaglia, G., Tsang, W. W. (2000). A simple method for generating gamma variables. *ACM Trans. Math. Softw.* 26(3), 363–372.
- Marzocchi, W., Sandri, L. (2003). A review and new insights on the estimation of the b-value and its uncertainty. *Ann. Geophys.* 46(6), 1271–1282.
- Tinti, S., Mulargia, F. (1987). Confidence intervals of b values for grouped magnitudes. *BSSA* 77(6), 2125–2134.
- Utsu, T. (1965). A method for determining the value of b in a formula log n = a − bM showing the magnitude–frequency relation for earthquakes. *Geophys. Bull. Hokkaido Univ.* 13, 99–103.

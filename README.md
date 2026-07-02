# ⚠️ Dikkat

Bu uygulama arka planda **AutoHotkey** kullanır. Bu nedenle bazı çevrim içi oyunlar veya anti-cheat sistemleri tarafından beklenmeyen davranışlar görülebilir. Uygulamayı kullanmadan önce bunun farkında olmanız önerilir.

---

# ClipTranslate

## Açıklama

**ClipTranslate**, Windows için geliştirilmiş hafif bir çeviri uygulamasıdır. Seçtiğiniz metni **Ctrl + Shift + X** kısayolu ile anında İngilizce'ye çevirir ve sonucu otomatik olarak panoya kopyalar.

---

## Kurulum

Gerekli yazılımlar:

- [Python](https://www.python.org/downloads/windows/)
- [AutoHotkey v2](https://www.autohotkey.com/)

Ardından proje klasöründe CMD açarak aşağıdaki komutu çalıştırın:

```bash
py -m pip install -r requirements.txt
```

---

## Özellikler

- Seçili metni anında İngilizce'ye çevirir.
- Sonucu otomatik olarak panoya kopyalar.
- Metin seçilebilen neredeyse tüm uygulamalarda çalışır (oyunlar, tarayıcılar, Discord, Not Defteri, Visual Studio Code vb.).
- Sistem tepsisinden **Windows ile Başlat** seçeneği etkinleştirilerek bilgisayar açıldığında otomatik olarak başlatılabilir.
- Çeviri tamamlandığında isteğe bağlı olarak masaüstü bildirimi gösterir.
- Sistem tepsisindeki **Aktif** seçeneği ile uygulama kapatılmadan çeviri özelliği açılıp kapatılabilir.
- Hafif bir uygulamadır ve genellikle **50 MB'den daha az RAM** kullanır.

---

## Kullanım

1. ClipTranslate'i çalıştırın.
2. Bilgisayarınızda AutoHotkey kurulu değilse uygulama sizi uyaracaktır.
3. İngilizce olmayan bir metin yazın.
4. Çevirmek istediğiniz metni seçin.
5. **Ctrl + Shift + X** tuşlarına basın.
6. Bildirimler açıksa **"Metin Çevrildi ve Panoya Kopyalandı"** bildirimi görüntülenir.
7. **Ctrl + V** ile çevrilen metni yapıştırın.

Artık seçtiğiniz metin İngilizce'ye çevrilmiş olacaktır.

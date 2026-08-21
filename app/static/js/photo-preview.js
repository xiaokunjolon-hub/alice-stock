/* 表单照片：新选文件即时缩略图预览 + 每张可删除（×）。
 * 挂载在 <form> 内的 input[type=file][name=photos] 上，删除后通过
 * DataTransfer 重建 input.files，保证提交内容与预览一致。
 * 已上传照片（服务端渲染的）不受影响。 */
(function () {
  var input = document.querySelector('form input[name="photos"]');
  if (!input) return;

  // 预览容器（自动创建，位于选择按钮下方）
  var box = document.getElementById('photoPreview');
  if (!box) {
    box = document.createElement('div');
    box.id = 'photoPreview';
    box.style.cssText = 'display:flex;flex-wrap:wrap;gap:8px;margin-top:10px;';
    input.parentNode.appendChild(box);
  }

  var files = [];

  input.addEventListener('change', function () {
    for (var i = 0; i < this.files.length; i++) files.push(this.files[i]);
    render();
    sync();
  });

  function render() {
    box.innerHTML = '';
    files.forEach(function (f, idx) {
      var wrap = document.createElement('div');
      wrap.style.cssText = 'position:relative;display:inline-block;';

      var img = document.createElement('img');
      img.src = URL.createObjectURL(f);
      img.style.cssText = 'width:72px;height:72px;object-fit:cover;' +
        'border-radius:6px;border:1px solid #e0e0e0;display:block;';

      var del = document.createElement('button');
      del.type = 'button';
      del.textContent = '×';
      del.title = '删除这张照片';
      del.style.cssText = 'position:absolute;top:-7px;right:-7px;width:20px;height:20px;' +
        'border-radius:50%;background:#c44;color:#fff;border:none;cursor:pointer;' +
        'font-size:14px;line-height:18px;padding:0;';
      del.onclick = function () {
        files.splice(idx, 1);
        render();
        sync();
      };

      wrap.appendChild(img);
      wrap.appendChild(del);
      box.appendChild(wrap);
    });
  }

  function sync() {
    if (!window.DataTransfer) return; // 老浏览器退化为仅预览
    var dt = new DataTransfer();
    files.forEach(function (f) { dt.items.add(f); });
    input.files = dt.files;
  }
})();

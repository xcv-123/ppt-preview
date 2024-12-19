// 获取DOM元素
const uploadBtn = document.getElementById('uploadBtn');
const fileInput = document.getElementById('fileInput');
const uploadArea = document.getElementById('uploadArea');
const uploadBox = document.querySelector('.upload-box');
const previewGrid = document.getElementById('previewGrid');
const selectedCount = document.getElementById('selectedCount');
const downloadBtn = document.getElementById('downloadBtn');

// 存储所有上传的PPT数据
let uploadedSlides = [];
const MAX_FILES = 10;

// 更新服务器地址
const SERVER_URL = 'http://49.235.159.198:5002';  // 替换为你的服务器IP

// 绑定上传按钮点击事件
uploadBtn.addEventListener('click', () => {
    fileInput.click();
});

// 处理文件选择
fileInput.addEventListener('change', handleFileSelect);

// 处理拖拽上传
uploadBox.addEventListener('dragover', (e) => {
    e.preventDefault();
    e.stopPropagation();
    uploadBox.style.borderColor = '#007AFF';
});

uploadBox.addEventListener('dragleave', (e) => {
    e.preventDefault();
    e.stopPropagation();
    uploadBox.style.borderColor = '#D2D2D7';
});

uploadBox.addEventListener('drop', (e) => {
    e.preventDefault();
    e.stopPropagation();
    uploadBox.style.borderColor = '#D2D2D7';
    
    const files = Array.from(e.dataTransfer.files).filter(file => 
        file.type === 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
    );
    
    handleFiles(files);
});

// 处理文件选择
function handleFileSelect(e) {
    const files = Array.from(e.target.files);
    handleFiles(files);
}

// 处理文件上传
async function handleFiles(files) {
    if (files.length === 0) {
        showMessage('请选择PPT文件');
        return;
    }
    
    if (files.length > MAX_FILES) {
        showMessage(`最多只能上传${MAX_FILES}个文件`);
        return;
    }
    
    fileInput.value = '';
    showUploadProgress();
    
    for (const file of files) {
        try {
            // 检查服务器是否在线
            try {
                const healthCheck = await fetch(`${SERVER_URL}/health`);
                if (!healthCheck.ok) {
                    throw new Error('服务器未响应');
                }
            } catch (error) {
                throw new Error('无法连接到服务器，请确保Python服务器已启动');
            }
            
            const formData = new FormData();
            formData.append('file', file);
            
            const response = await fetch(`${SERVER_URL}/upload`, {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || '上传失败');
            }
            
            const data = await response.json();
            
            // 创建每一页的预览
            for (const preview of data.previews) {
                await createSlidePreview({
                    fileName: file.name,
                    slideNumber: preview.slideNumber,
                    totalSlides: data.totalSlides,
                    imageData: preview.imageData,
                    sourcePath: preview.sourcePath
                });
            }
            
        } catch (error) {
            console.error('PPT处理失败:', error);
            showMessage(error.message || `${file.name} 处理失败`);
        }
    }
    
    resetUploadArea();
}

// 创建幻灯片预览
async function createSlidePreview(slideData) {
    const card = document.createElement('div');
    card.className = 'slide-card';
    
    // 创建预览容器
    const previewContainer = document.createElement('div');
    previewContainer.className = 'slide-preview';
    
    // 创建预览图片
    const preview = document.createElement('img');
    preview.className = 'pptx-preview';
    preview.src = `data:image/jpeg;base64,${slideData.imageData}`;
    previewContainer.appendChild(preview);
    
    // 添加复选框
    const checkboxContainer = document.createElement('label');
    checkboxContainer.className = 'checkbox-container';
    checkboxContainer.innerHTML = `
        <input type="checkbox" class="slide-checkbox">
        <span class="checkmark"></span>
    `;
    previewContainer.appendChild(checkboxContainer);
    
    // 添加信息区域
    const info = document.createElement('div');
    info.className = 'slide-info';
    info.innerHTML = `
        <p class="file-name">${slideData.fileName}</p>
        <p class="slide-number">第 ${slideData.slideNumber} 页 / 共 ${slideData.totalSlides} 页</p>
    `;
    
    // 组装卡片
    card.appendChild(previewContainer);
    card.appendChild(info);
    
    // 存储幻灯片数据
    uploadedSlides.push({
        ...slideData,
        element: card,
        sourcePath: slideData.sourcePath
    });
    
    // 处理选择事件
    const checkbox = card.querySelector('.slide-checkbox');
    checkbox.addEventListener('change', () => {
        updateSelection();
    });
    
    // 添加到网格
    previewGrid.appendChild(card);
}

// 更新选择状态
function updateSelection() {
    const selectedSlides = document.querySelectorAll('.slide-checkbox:checked').length;
    selectedCount.textContent = selectedSlides;
    downloadBtn.disabled = selectedSlides === 0;
}

// 显示上传进度
function showUploadProgress() {
    uploadBox.innerHTML = `
        <div class="upload-progress">
            <div class="progress-bar"></div>
            <p>正在处理PPT文件...</p>
        </div>
    `;
}

// 重置上传区域
function resetUploadArea() {
    uploadBox.innerHTML = `
        <img src="assets/upload-icon.svg" alt="上传图标">
        <p>拖拽PPT文件到这里，或点击上传</p>
        <p class="upload-tip">支持个或最多10个PPT文件</p>
        <input type="file" id="fileInput" multiple accept=".pptx" hidden>
    `;
}

// 显示消息提示
function showMessage(message) {
    const toast = document.createElement('div');
    toast.className = 'toast-message';
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 2000);
}

// 绑定下载按钮事件
downloadBtn.addEventListener('click', async () => {
    const selectedSlides = Array.from(document.querySelectorAll('.slide-checkbox:checked'))
        .map(checkbox => {
            const card = checkbox.closest('.slide-card');
            const index = Array.from(previewGrid.children).indexOf(card);
            return uploadedSlides[index];
        });
    
    if (selectedSlides.length === 0) {
        showMessage('请选择要下载的页面');
        return;
    }
    
    try {
        showMessage('正在生成PPT...');
        
        const response = await fetch(`${SERVER_URL}/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                slides: selectedSlides
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || '生成PPT失败');
        }
        
        // 获取文件blob
        const blob = await response.blob();
        
        // 创建下载链接
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = '新PPT.pptx';
        document.body.appendChild(a);
        a.click();
        
        // 清理
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        showMessage('下载成功');
        
    } catch (error) {
        console.error('生成PPT失败:', error);
        showMessage(error.message || '生成PPT失败，请重试');
    }
});
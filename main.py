import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="TikTok Downloader API",
    description="API tải video TikTok không logo tốc độ cao",
    version="1.0.0"
)

# Cấu hình CORS để có thể gọi API từ bất cứ đâu (Ví dụ: gọi từ Phím tắt iOS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TIKWM_API = "https://api.tikwm.com/api/"

@app.get("/api/download")
async def download_tiktok(url: str = Query(..., description="Link video TikTok (vt.tiktok, vm.tiktok, hoặc vlink)")):
    if not url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="Định dạng URL không hợp lệ")

    payload = {"url": url}
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(TIKWM_API, data=payload)
            
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail="Không thể kết nối đến server tải video")
                
            res_data = response.json()
            
            if res_data.get("code") != 0 or "data" not in res_data:
                raise HTTPException(status_code=400, detail=res_data.get("msg", "Không tìm thấy video hoặc link lỗi"))
            
            video_data = res_data["data"]
            
            # Trả về các thông tin cần thiết
            return {
                "status": "success",
                "title": video_data.get("title"),
                "cover": video_data.get("cover"),
                "video_no_watermark": video_data.get("play"),       # Link video ko logo
                "video_watermark": video_data.get("wmplay"),       # Link video có logo
                "music": video_data.get("music"),                 # Link nhạc nền
                "author": {
                    "nickname": video_data.get("author", {}).get("nickname"),
                    "avatar": video_data.get("author", {}).get("avatar")
                }
            }
            
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Lỗi kết nối mạng: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống: {str(e)}")

@app.get("/")
def read_root():
    return {"message": "API đang hoạt động ổn định. Truy cập /docs để xem tài liệu chi tiết."}

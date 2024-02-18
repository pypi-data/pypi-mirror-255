# -*- coding: utf-8 -*-

# https://blog.csdn.net/ljp1919/article/details/131925099


from huggingface_hub import snapshot_download
from dramkit.iotools import make_dir


def load_hf(repo_id: str,
            save_dir: str,
            hf_token: str = None,
            proxies: dict = None):
    make_dir(save_dir)
    snapshot_download(
        repo_id=repo_id,
        local_dir=save_dir,
        local_dir_use_symlinks=False, # 本地模型使用文件保存，而非blob形式保存？
        token=hf_token,
        proxies=proxies
    )


if __name__ == '__main__':
    
    hf_token = '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'
    
    repo_id = 'THUDM/chatglm3-6b'
    save_dir = '../../../llm/chatglm/chatglm3-6b'
    
    load_hf(repo_id, save_dir, hf_token=hf_token)
    
    
    
    
    
    

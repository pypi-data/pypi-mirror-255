# -*- coding: utf-8 -*-

# https://zhuanlan.zhihu.com/p/648127076
# https://gist.github.com/xiabingquan/eb2ceb583a1e8858c23da23ac7a4a340


import numpy as np
import torch
import torch.nn as nn


def get_len_mask(max_len: int,
                 feat_lens: torch.Tensor,
                 device: torch.device
                 ) -> torch.Tensor:
    '''
    判断每个位置是否需要mask
    
    Parameters
    ----------
    max_len : int
        the length of the whole seqeunce
    feat_lens : torch.Tensor
        每个样本的长度
    
    Examples
    --------
    >>> m = get_len_mask(4, torch.tensor([2, 3, 4]), 'cpu')
    >>> m = m.int()
    >>> m
    tensor([[[0, 0, 1, 1],
             [0, 0, 1, 1],
             [0, 0, 1, 1],
             [0, 0, 1, 1]],

            [[0, 0, 0, 1],
             [0, 0, 0, 1],
             [0, 0, 0, 1],
             [0, 0, 0, 1]],

            [[0, 0, 0, 0],
             [0, 0, 0, 0],
             [0, 0, 0, 0],
             [0, 0, 0, 0]]], dtype=torch.int32)
    '''
    b = feat_lens.shape[0]
    attn_mask = torch.ones((b, max_len, max_len), device=device)
    for i in range(b):
        attn_mask[i, :, :feat_lens[i]] = 0
    return attn_mask.to(torch.bool)


def get_subsequent_mask(b: int,
                        max_len: int,
                        device: torch.device
                        ) -> torch.Tensor:
    '''
    Causal mask
    
    Parameters
    ----------
    b : int
        batch-size
    max_len : int
        the length of the whole seqeunce
    device : cuda or cpu
    
    Examples
    --------
    >>> m = get_subsequent_mask(3, 4, 'cpu')
    >>> m
    
    '''
    return torch.triu(torch.ones((b, max_len, max_len), device=device),
                      diagonal=1).to(torch.bool) # or .to(torch.uint8)


def get_enc_dec_mask(b: int,
                     max_feat_len: int,
                     feat_lens: torch.Tensor,
                     max_label_len: int,
                     device: torch.device
                     ) -> torch.Tensor:
    attn_mask = torch.zeros((b, max_label_len, max_feat_len),
                            device=device) # (b, seq_q, seq_k)
    for i in range(b):
        attn_mask[i, :, feat_lens[i]:] = 1
    return attn_mask.to(torch.bool)


def pos_sinusoid_embedding(seq_len: int,
                           d_model: int
                           ) -> torch.Tensor:
    '''位置编码'''
    embeddings = torch.zeros((seq_len, d_model))
    for i in range(d_model):
        f = torch.sin if i % 2 == 0 else torch.cos
        embeddings[:, i] = f(torch.arange(0, seq_len) / np.power(1e4, 2 * (i // 2) / d_model))
    return embeddings.float()


class MultiHeadAttention(nn.Module):
    '''多头自注意力层'''
    
    def __init__(self, d_k, d_v, d_model, n_head, p=0.):
        super(MultiHeadAttention, self).__init__()
        self.d_model = d_model
        self.d_k = d_k
        self.d_v = d_v
        self.n_head = n_head
        self.dropout = nn.Dropout(p)
        
        # linear projections
        self.W_Q = nn.Linear(d_model, d_k * n_head)
        self.W_K = nn.Linear(d_model, d_k * n_head)
        self.W_V = nn.Linear(d_model, d_v * n_head)
        self.W_out = nn.Linear(d_v * n_head, d_model)

        # Normalization
        # References: <<Delving Deep into Rectifiers: Surpassing Human-Level Performance on ImageNet Classification>>
        nn.init.normal_(self.W_Q.weight, mean=0, std=np.sqrt(2.0 / (d_model + d_k)))
        nn.init.normal_(self.W_K.weight, mean=0, std=np.sqrt(2.0 / (d_model + d_k)))
        nn.init.normal_(self.W_V.weight, mean=0, std=np.sqrt(2.0 / (d_model + d_v)))
        nn.init.normal_(self.W_out.weight, mean=0, std=np.sqrt(2.0 / (d_model + d_v)))

    def forward(self, Q, K, V, attn_mask, **kwargs):
        N = Q.size(0) # Q样本量
        q_len, k_len = Q.size(1), K.size(1) # ？
        d_k, d_v = self.d_k, self.d_v
        n_head = self.n_head

        # multi_head split
        Q = self.W_Q(Q).view(N, -1, n_head, d_k).transpose(1, 2)
        K = self.W_K(K).view(N, -1, n_head, d_k).transpose(1, 2)
        V = self.W_V(V).view(N, -1, n_head, d_v).transpose(1, 2)
        
        # pre-process mask 
        if attn_mask is not None:
            assert attn_mask.size() == (N, q_len, k_len)
            attn_mask = attn_mask.unsqueeze(1).repeat(1, n_head, 1, 1) # broadcast
            attn_mask = attn_mask.bool()

        # calculate attention weight
        scores = torch.matmul(Q, K.transpose(-1, -2)) / np.sqrt(d_k)
        if attn_mask is not None:
            scores.masked_fill_(attn_mask, -1e4)
        attns = torch.softmax(scores, dim=-1) # attention weights
        attns = self.dropout(attns)

        # calculate output
        output = torch.matmul(attns, V)

        # multi_head merge
        output = output.transpose(1, 2).contiguous().reshape(N, -1, d_v * n_head)
        output = self.W_out(output)

        return output
    
    
class PoswiseFFN(nn.Module):
    '''全连接层'''
    
    def __init__(self, d_model, d_ff, p=0.0):
        super(PoswiseFFN, self).__init__()
        self.d_model = d_model
        self.d_ff = d_ff
        self.conv1 = nn.Conv1d(d_model, d_ff, 1, 1, 0)
        self.conv2 = nn.Conv1d(d_ff, d_model, 1, 1, 0)
        self.relu = nn.ReLU(inplace=True)
        self.dropout = nn.Dropout(p=p)

    def forward(self, X):
        out = self.conv1(X.transpose(1, 2)) # (N, d_model, seq_len) -> (N, d_ff, seq_len)
        out = self.relu(out)
        out = self.conv2(out).transpose(1, 2) # (N, d_ff, seq_len) -> (N, d_model, seq_len)
        out = self.dropout(out)
        return out


class EncoderLayer(nn.Module):
    '''编码层'''
    
    def __init__(self,
                 dim: int,
                 n_head: int,
                 dff: int,
                 dropout_posffn, dropout_attn):
        '''
        Parameters
        ----------
        dim : int
            input dimension
        n : int
            number of attention heads
        dff : int
            dimention of PosFFN (Positional FeedForward)
        dropout_posffn : 
            dropout ratio of PosFFN
        dropout_attn : 
            dropout ratio of attention module
        '''
        assert dim % n_head == 0
        hdim = dim // n_head # dimension of each attention head
        super(EncoderLayer, self).__init__()
        # LayerNorm
        self.norm1 = nn.LayerNorm(dim)
        self.norm2 = nn.LayerNorm(dim)
        # MultiHeadAttention
        self.multi_head_attn = MultiHeadAttention(hdim, hdim, dim, n_head, dropout_attn)
        # Position-wise Feedforward Neural Network
        self.poswise_ffn = PoswiseFFN(dim, dff, p=dropout_posffn)

    def forward(self, enc_in, attn_mask):
        # reserve original input for later residual connections
        residual = enc_in
        # MultiHeadAttention forward
        context = self.multi_head_attn(enc_in, enc_in, enc_in, attn_mask)
        # residual connection and norm
        out = self.norm1(residual + context)
        residual = out
        # position-wise feedforward
        out = self.poswise_ffn(out)
        # residual connection and norm
        out = self.norm2(residual + out)
        return out


class Encoder(nn.Module):
    '''编码器'''
    
    def __init__(self,
                 dropout_emb,
                 dropout_posffn,
                 dropout_attn,
                 n_layer,
                 enc_dim,
                 n_head,
                 dff,
                 tgt_len
                 ):
        '''
        Parameters
        ----------
        dropout_emb : 
            dropout ratio of Position Embeddings
        dropout_posffn : 
            dropout ratio of PosFFN
        dropout_attn : 
            dropout ratio of attention module
        n_layer : 
            number of encoder layers
        enc_dim : 
            input dimension of encoder
        n_head : 
            number of attention heads
        dff : 
            dimensionf of PosFFN
        tgt_len : 
            the maximum length of sequences
        '''
        super(Encoder, self).__init__()
        # The maximum length of input sequence
        self.tgt_len = tgt_len
        self.pos_emb = nn.Embedding.from_pretrained(pos_sinusoid_embedding(tgt_len, enc_dim),
                                                    freeze=True)
        self.emb_dropout = nn.Dropout(dropout_emb)
        self.layers = nn.ModuleList(
            [EncoderLayer(enc_dim, n_head, dff, dropout_posffn, dropout_attn) for _ in range(n_layer)])
    
    def forward(self, X, X_lens, mask=None):
        # add position embedding
        batch_size, seq_len, d_model = X.shape
        out = X + self.pos_emb(torch.arange(seq_len, device=X.device)) # (batch_size, seq_len, d_model)
        out = self.emb_dropout(out)
        # encoder layers
        for layer in self.layers:
            out = layer(out, mask)
        return out

    
class DecoderLayer(nn.Module):
    '''解码层'''
    
    def __init__(self, dim, n_head, dff, dropout_posffn, dropout_attn):
        '''
        Parameters
        ----------
        dim : 
            input dimension
        n_head : 
            number of attention heads
        dff : 
            dimention of PosFFN (Positional FeedForward)
        dropout_posffn : 
            dropout ratio of PosFFN
        dropout_attn : 
            dropout ratio of attention module
        '''
        super(DecoderLayer, self).__init__()
        assert dim % n_head == 0
        hdim = dim // n_head
        # LayerNorms
        self.norm1 = nn.LayerNorm(dim)
        self.norm2 = nn.LayerNorm(dim)
        self.norm3 = nn.LayerNorm(dim)
        # Position-wise Feed-Forward Networks
        self.poswise_ffn = PoswiseFFN(dim, dff, p=dropout_posffn)
        # MultiHeadAttention, both self-attention and encoder-decoder cross attention)
        self.dec_attn = MultiHeadAttention(hdim, hdim, dim, n_head, dropout_attn)
        self.enc_dec_attn = MultiHeadAttention(hdim, hdim, dim, n_head, dropout_attn)

    def forward(self, dec_in, enc_out, dec_mask, dec_enc_mask, cache=None, freqs_cis=None):
        # decoder's self-attention
        residual = dec_in
        context = self.dec_attn(dec_in, dec_in, dec_in, dec_mask)
        dec_out = self.norm1(residual + context)
        # encoder-decoder cross attention
        residual = dec_out
        context = self.enc_dec_attn(dec_out, enc_out, enc_out, dec_enc_mask)
        dec_out = self.norm2(residual + context)
        # position-wise feed-forward networks
        residual = dec_out
        out = self.poswise_ffn(dec_out)
        dec_out = self.norm3(residual + out)
        return dec_out


class Decoder(nn.Module):
    '''解码器'''
    
    def __init__(self,
                 dropout_emb,
                 dropout_posffn,
                 dropout_attn,
                 n_layer,
                 dec_dim,
                 n_head,
                 dff,
                 tgt_len,
                 tgt_vocab_size
                 ):
        '''
        Parameters
        ----------
        dropout_emb : 
            dropout ratio of Position Embeddings
        dropout_posffn : 
            dropout ratio of PosFFN
        dropout_attn : 
            dropout ratio of attention module
        n_layer : 
            number of encoder layers
        dec_dim : 
            input dimension of decoder
        n_head : 
            number of attention heads
        dff : 
            dimensionf of PosFFN
        tgt_len : 
            the target length to be embedded
        tgt_vocab_size : 
            the target vocabulary size
        '''
        super(Decoder, self).__init__()
        # output embedding
        self.tgt_emb = nn.Embedding(tgt_vocab_size, dec_dim)
        self.dropout_emb = nn.Dropout(p=dropout_emb) # embedding dropout
        # position embedding
        self.pos_emb = nn.Embedding.from_pretrained(pos_sinusoid_embedding(tgt_len, dec_dim),
                                                    freeze=True)
        # decoder layers
        self.layers = nn.ModuleList(
            [DecoderLayer(dec_dim, n_head, dff, dropout_posffn, dropout_attn) for _ in range(n_layer)])

    def forward(self, labels, enc_out, dec_mask, dec_enc_mask, cache=None):
        # output embedding and position embedding
        tgt_emb = self.tgt_emb(labels)
        pos_emb = self.pos_emb(torch.arange(labels.size(1), device=labels.device))
        dec_out = self.dropout_emb(tgt_emb + pos_emb)
        # decoder layers
        for layer in self.layers:
            dec_out = layer(dec_out, enc_out, dec_mask, dec_enc_mask)
        return dec_out


class Transformer(nn.Module):
    '''Transformer'''
    
    def __init__(self,
                 frontend: nn.Module, 
                 encoder: nn.Module, 
                 decoder: nn.Module,
                 dec_out_dim: int,
                 vocab: int
                 ) -> None:
        super().__init__()
        self.frontend = frontend # feature extractor
        self.encoder = encoder
        self.decoder = decoder
        self.linear = nn.Linear(dec_out_dim, vocab)

    def forward(self,
                X: torch.Tensor,
                X_lens: torch.Tensor,
                labels: torch.Tensor
                ):
        X_lens, labels = X_lens.long(), labels.long()
        b = X.size(0)
        device = X.device
        # frontend
        out = self.frontend(X)
        max_feat_len = out.size(1) # compute after frontend because of optional subsampling
        max_label_len = labels.size(1)
        # encoder
        enc_mask = get_len_mask(max_feat_len, X_lens, device)
        enc_out = self.encoder(out, X_lens, enc_mask)
        # decoder
        dec_mask = get_subsequent_mask(b, max_label_len, device)
        dec_enc_mask = get_enc_dec_mask(b, max_feat_len, X_lens, max_label_len, device)
        dec_out = self.decoder(labels, enc_out, dec_mask, dec_enc_mask)
        logits = self.linear(dec_out)
        return logits


if __name__ == '__main__':
    # constants
    batch_size = 16 # batch size
    max_feat_len = 100 # the maximum length of input sequence
    fbank_dim = 80 # the dimension of input feature
    hidden_dim = 512 # the dimension of hidden layer
    vocab_size = 26 # the size of vocabulary
    max_lable_len = 120 # the maximum length of output sequence

    # dummy data
    fbank_feature = torch.randn(batch_size, max_feat_len, fbank_dim)        # input sequence
    feat_lens = torch.randint(1, max_feat_len, (batch_size,))               # the length of each input sequence in the batch
    labels = torch.randint(0, 26, (batch_size, max_lable_len))              # output sequence
    label_lens = torch.randint(1, 10, (batch_size,))                        # the length of each output sequence in the batch

    # model
    feature_extractor = nn.Linear(fbank_dim, hidden_dim)                    # a single layer to simulate the audio feature extractor
    encoder = Encoder(dropout_emb=0.1,
                      dropout_posffn=0.1,
                      dropout_attn=0.0,
                      n_layer=6,
                      enc_dim=hidden_dim,
                      n_head=8,
                      dff=2048,
                      tgt_len=2048)
    decoder = Decoder(dropout_emb=0.1,
                      dropout_posffn=0.1,
                      dropout_attn=0.0,
                      n_layer=6,
                      dec_dim=hidden_dim,
                      n_head=8,
                      dff=2048,
                      tgt_len=2048,
                      tgt_vocab_size=vocab_size)
    transformer = Transformer(feature_extractor,
                              encoder,
                              decoder,
                              hidden_dim,
                              vocab_size)
    
    # forward check
    logits = transformer(fbank_feature, feat_lens, labels)
    print(logits.shape) # (batch_size, max_label_len, vocab_size)

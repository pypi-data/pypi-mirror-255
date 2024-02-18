#pragma once

// @generated from /usr1/03/workspace/j_C88Hdi7d/pytorch/codegen/autograd/templates/VariableType.h

#include <cstdint> // for size_t
#include <functional> // for function
#include <memory> // for unique_ptr
#include <string>
#include <vector>

#include <ATen/core/Tensor.h>
#include <ATen/Context.h>

#include <c10/util/intrusive_ptr.h>

#include <torch/csrc/Export.h>
#include <torch/csrc/autograd/autograd_not_implemented_fallback.h>

namespace at {
  struct Quantizer;
};

namespace at_npu { namespace autograd {

using Variable = at::Tensor;
using at::Context;
using at::Device;
using at::Dimname;
using at::DimnameList;
using at::Generator;
using at::IntArrayRef;
using at::MemoryFormat;
using at::QScheme;
using at::Scalar;
using at::ScalarType;
using at::Storage;
using at::Tensor;
using at::TensorList;
using at::TensorOptions;
using at::Quantizer;
// This is temporary typedef to enable Quantizer in aten native function API
// we'll remove them when we are actually exposing Quantizer class
// to frontend
using ConstQuantizerPtr = const c10::intrusive_ptr<Quantizer>&;
using c10::optional;

namespace VariableType {
  TORCH_API std::vector<at::DeprecatedTypeProperties*> allCPUTypes();

  at::Tensor& unpack(Tensor& t, const char* name, int pos);
  const at::Tensor& unpack(const Tensor& t, const char* name, int pos);
  at::Tensor unpack_opt(const Tensor& t, const char* name, int pos);
  std::vector<at::Tensor> unpack(at::TensorList tl, const char *name, int pos);

  at::Tensor _npu_format_cast(c10::DispatchKeySet ks, const at::Tensor & self, int64_t acl_format);
  ::std::tuple<at::Tensor,at::Tensor> npu_geglu(c10::DispatchKeySet ks, const at::Tensor & self, int64_t dim, int64_t approximate, bool activate_left);
  ::std::tuple<at::Tensor,at::Tensor,at::Tensor,at::Tensor> npu_add_layer_norm(c10::DispatchKeySet ks, const at::Tensor & x1, const at::Tensor & x2, const at::Tensor & gamma, const at::Tensor & beta, double epsilon, bool additional_output);
  ::std::tuple<at::Tensor,at::Tensor> npu_rms_norm(c10::DispatchKeySet ks, const at::Tensor & self, const at::Tensor & gamma, double epsilon);
  at::Tensor npu_swiglu(c10::DispatchKeySet ks, const at::Tensor & self, int64_t dim);
  ::std::tuple<at::Tensor,at::Tensor,at::Tensor> npu_deep_norm(c10::DispatchKeySet ks, const at::Tensor & x, const at::Tensor & gx, const at::Tensor & beta, const at::Tensor & gamma, double alpha, double epsilon);
  ::std::tuple<at::Tensor,at::Tensor,at::Tensor> npu_fused_attention_score_fwd(c10::DispatchKeySet ks, const at::Tensor & query_layer, const at::Tensor & key_layer, const at::Tensor & value_layer, const at::Tensor & attention_mask, const at::Scalar & scale, double keep_prob, bool query_transpose, bool key_transpose, bool bmm_score_transpose_a, bool bmm_score_transpose_b, bool value_transpose, bool dx_transpose);
  at::Tensor npu_convolution(c10::DispatchKeySet ks, const at::Tensor & input, const at::Tensor & weight, const c10::optional<at::Tensor> & bias, at::IntArrayRef stride, at::IntArrayRef padding, at::IntArrayRef dilation, int64_t groups);
  at::Tensor npu_convolution_transpose(c10::DispatchKeySet ks, const at::Tensor & input, const at::Tensor & weight, const c10::optional<at::Tensor> & bias, at::IntArrayRef padding, at::IntArrayRef output_padding, at::IntArrayRef stride, at::IntArrayRef dilation, int64_t groups);
  at::Tensor fast_gelu(c10::DispatchKeySet ks, const at::Tensor & self);
  at::Tensor npu_confusion_transpose(c10::DispatchKeySet ks, const at::Tensor & self, at::IntArrayRef perm, at::IntArrayRef shape, bool transpose_first);
  at::Tensor npu_ps_roi_pooling(c10::DispatchKeySet ks, const at::Tensor & self, const at::Tensor & rois, double spatial_scale, int64_t group_size, int64_t output_dim);
  at::Tensor npu_linear(c10::DispatchKeySet ks, const at::Tensor & input, const at::Tensor & weight, const c10::optional<at::Tensor> & bias);
  ::std::tuple<at::Tensor,at::Tensor> _npu_dropout(c10::DispatchKeySet ks, const at::Tensor & self, double p);
  at::Tensor npu_softmax_cross_entropy_with_logits(c10::DispatchKeySet ks, const at::Tensor & self, const at::Tensor & labels);
  ::std::tuple<at::Tensor,at::Tensor> npu_max_dim(c10::DispatchKeySet ks, const at::Tensor & self, int64_t dim, bool keepdim);
  at::Tensor npu_bmmV2(c10::DispatchKeySet ks, const at::Tensor & self, const at::Tensor & mat2, at::IntArrayRef output_sizes);
  at::Tensor npu_dtype_cast(c10::DispatchKeySet ks, const at::Tensor & self, at::ScalarType dtype);
  at::Tensor npu_silu(c10::DispatchKeySet ks, const at::Tensor & self);
  at::Tensor & npu_silu_(c10::DispatchKeySet ks, at::Tensor & self);
  ::std::tuple<at::Tensor,at::Tensor,at::Tensor,at::Tensor,at::Tensor,at::Tensor> npu_gru(c10::DispatchKeySet ks, const at::Tensor & input, const at::Tensor & hx, const at::Tensor & weight_input, const at::Tensor & weight_hidden, const at::Tensor & bias_input, const at::Tensor & bias_hidden, const at::Tensor & seq_length, bool has_biases, int64_t num_layers, double dropout, bool train, bool bidirectional, bool batch_first);
  at::Tensor npu_mish(c10::DispatchKeySet ks, const at::Tensor & self);
  ::std::tuple<at::Tensor,at::Tensor> npu_min_dim(c10::DispatchKeySet ks, const at::Tensor & self, int64_t dim, bool keepdim);
  ::std::tuple<at::Tensor,at::Tensor> npu_deformable_conv2d(c10::DispatchKeySet ks, const at::Tensor & input, const at::Tensor & weight, const at::Tensor & offset, const c10::optional<at::Tensor> & bias, at::IntArrayRef kernel_size, at::IntArrayRef stride, at::IntArrayRef padding, at::IntArrayRef dilation, int64_t groups, int64_t deformable_groups, bool modulated);
  at::Tensor npu_giou(c10::DispatchKeySet ks, const at::Tensor & self, const at::Tensor & gtboxes, bool trans, bool is_cross, int64_t mode);
  at::Tensor npu_diou(c10::DispatchKeySet ks, const at::Tensor & self, const at::Tensor & gtboxes, bool trans, bool is_cross, int64_t mode);
  ::std::tuple<at::Tensor,at::Tensor,at::Tensor,at::Tensor,at::Tensor,at::Tensor,at::Tensor,at::Tensor> npu_lstm(c10::DispatchKeySet ks, const at::Tensor & input, const at::Tensor & weight, const at::Tensor & bias, const at::Tensor & seq_mask, const at::Tensor & h, const at::Tensor & c, bool has_biases, int64_t num_layers, double dropout, bool train, bool bidirectional, bool batch_first, bool flag_seq, bool direction);
  ::std::tuple<at::Tensor,at::Tensor,at::Tensor,at::Tensor,at::Tensor,at::Tensor,at::Tensor,at::Tensor> npu_lstm_data(c10::DispatchKeySet ks, const at::Tensor & input, const at::Tensor & batch_sizes, const at::Tensor & weight, const at::Tensor & bias, const at::Tensor & seq_mask, const at::Tensor & h, const at::Tensor & c, bool has_biases, int64_t num_layers, double dropout, bool train, bool bidirectional, bool batch_first, bool flag_seq, bool direction);
  ::std::tuple<at::Tensor,at::Tensor> _dropout_with_byte_mask(c10::DispatchKeySet ks, const at::Tensor & self, double p);
  ::std::tuple<at::Tensor,at::Tensor,at::Tensor> npu_dropout_with_add_softmax(c10::DispatchKeySet ks, const at::Tensor & self, const at::Tensor & x1, const at::Scalar & alpha, double prob, int64_t dim);
  at::Tensor npu_scaled_masked_softmax(c10::DispatchKeySet ks, const at::Tensor & x, const at::Tensor & mask, const at::Scalar & scale, bool fixed_triu_mask);
  ::std::tuple<at::Tensor,at::Tensor,at::Tensor,at::Tensor,at::Tensor,at::Tensor,at::Tensor,at::Tensor> npu_multi_head_attention(c10::DispatchKeySet ks, const at::Tensor & query, const at::Tensor & key, const at::Tensor & value, const at::Tensor & query_weight, const at::Tensor & key_weight, const at::Tensor & value_weight, const at::Tensor & attn_mask, const at::Tensor & out_proj_weight, const c10::optional<at::Tensor> & query_bias, const c10::optional<at::Tensor> & key_bias, const c10::optional<at::Tensor> & value_bias, const c10::optional<at::Tensor> & out_proj_bias, const c10::optional<at::Tensor> & dropout_mask, int64_t attn_head_num, int64_t attn_dim_per_head, int64_t src_len, int64_t tgt_len, double dropout_prob, bool softmax_use_float);
  ::std::tuple<at::Tensor,at::Tensor,at::Tensor,at::Tensor,int64_t,int64_t,int64_t> npu_fusion_attention(c10::DispatchKeySet ks, const at::Tensor & query, const at::Tensor & key, const at::Tensor & value, int64_t head_num, c10::string_view input_layout, const c10::optional<at::Tensor> & pse, const c10::optional<at::Tensor> & padding_mask, const c10::optional<at::Tensor> & atten_mask, double scale, double keep_prob, int64_t pre_tockens, int64_t next_tockens, int64_t inner_precise, at::OptionalIntArrayRef prefix, at::OptionalIntArrayRef actual_seq_qlen, at::OptionalIntArrayRef actual_seq_kvlen, int64_t sparse_mode, bool gen_mask_parallel, bool sync);
  ::std::tuple<at::Tensor,at::Tensor> npu_dropout_do_mask(c10::DispatchKeySet ks, const at::Tensor & self, const at::Tensor & mask, double p);
  ::std::tuple<at::Tensor,at::Tensor,at::Tensor,at::Tensor,at::Tensor,at::Tensor,at::Tensor,at::Tensor> npu_lstm_cell(c10::DispatchKeySet ks, const at::Tensor & input, const at::Tensor & w_ih, const at::Tensor & w_hh, const at::Tensor & h, const at::Tensor & c, const c10::optional<at::Tensor> & b_ih, const c10::optional<at::Tensor> & b_hh);
  at::Tensor npu_rotary_mul(c10::DispatchKeySet ks, const at::Tensor & self, const at::Tensor & r1, const at::Tensor & r2);
  ::std::tuple<at::Tensor,at::Tensor> _npu_ciou(c10::DispatchKeySet ks, const at::Tensor & self, const at::Tensor & gtboxes, bool trans, bool is_cross, int64_t mode, bool atan_sub_flag);
  ::std::tuple<at::Tensor,at::Tensor,at::Tensor,at::Tensor,int64_t,int64_t,int64_t> npu_fusion_attention_v3(c10::DispatchKeySet ks, const at::Tensor & x, const at::Tensor & weight, int64_t head_num, c10::string_view input_layout, int64_t head_size, const c10::optional<at::Tensor> & bias, const c10::optional<at::Tensor> & pse, const c10::optional<at::Tensor> & atten_mask, at::OptionalIntArrayRef prefix, double scale_qk, double scale_q, double scale_k, double keep_prob, int64_t pre_tockens, int64_t next_tockens, int64_t sparse_mode, int64_t pse_type, bool gen_mask_parallel, bool sync);
  ::std::tuple<at::Tensor,at::Tensor,int64_t,int64_t,int64_t> npu_multi_head_attention_v2(c10::DispatchKeySet ks, const at::Tensor & query, const at::Tensor & key, const at::Tensor & value, const c10::optional<at::Tensor> & atten_mask, const c10::optional<at::Tensor> & alibi_mask, double scale, int64_t head_num, c10::string_view input_layout, double keep_prob, int64_t pre_tokens, int64_t next_tokens, bool gen_mask_parallel, bool sync);
};

}} // namespace at_npu::autograd

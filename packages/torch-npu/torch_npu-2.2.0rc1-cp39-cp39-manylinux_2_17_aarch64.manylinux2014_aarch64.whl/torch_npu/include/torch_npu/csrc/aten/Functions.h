#pragma once

// @generated from ../../../../../../../usr1/02/workspace/j_herhM2p0/pytorch/codegen/autograd/templates/Functions.h

#include <ATen/ATen.h>
#include <ATen/core/functional.h>
#include <ATen/TensorGeometry.h>

#include <torch/csrc/autograd/function.h>
#include <torch/csrc/autograd/variable.h>
#include <torch/csrc/autograd/saved_variable.h>
#include <torch/csrc/Export.h>

#include <c10/core/SymIntArrayRef.h>

using namespace torch::autograd;

namespace at_npu { namespace autograd { namespace generated {

using at::Scalar;
using at::Tensor;
using at::IntArrayRef;
using at::ArrayRef;
using at::Type;
using at::TensorGeometry;
using at::ScalarType;
using c10::optional;
using c10::fmap;

inline std::vector<Tensor> unpack_list(at::ArrayRef<SavedVariable> xs) {
  // NB: we must explicitly do the conversion in the lambda, otherwise template
  // deduction will give a Tensor of Variable which is not convertible
  return fmap(xs, [](const SavedVariable& x) {
    return static_cast<Tensor>(x.unpack());
  });
}

inline c10::List<c10::optional<Tensor>> unpack_opt_list(at::ArrayRef<SavedVariable> xs) {
  torch::List<c10::optional<Tensor>> result;
  result.reserve(xs.size());
  for (const SavedVariable& v : xs) {
    result.push_back(v.unpack());
  }
  return result;
}

struct TypeAndSize {
    TypeAndSize() : options(at::TensorOptions()) {}
    /* implicit */
    TypeAndSize(const Tensor & t)
        : sizes(t.sizes().vec())
        , options(t.options()) {}

  Tensor zeros() { return at::zeros(sizes, options); }

private:
  std::vector<int64_t> sizes;
  at::TensorOptions options;
};

#ifdef _WIN32
struct NpuMultiHeadAttentionBackward0 : public TraceableFunction {
  TORCH_API NpuMultiHeadAttentionBackward0() = default;
#else
struct TORCH_API NpuMultiHeadAttentionBackward0 : public TraceableFunction {
#endif
  using TraceableFunction::TraceableFunction;
  variable_list apply(variable_list&& grads) override;
  std::string name() const override { return "NpuMultiHeadAttentionBackward0"; }
  void release_variables() override {
    std::lock_guard<std::mutex> lock(mutex_);
    key_.reset_data();
    key_bias_.reset_data();
    key_weight_.reset_data();
    out_proj_bias_.reset_data();
    out_proj_weight_.reset_data();
    query_.reset_data();
    query_bias_.reset_data();
    query_weight_.reset_data();
    value_.reset_data();
    value_bias_.reset_data();
    value_weight_.reset_data();
    result1_.reset_data();
    result2_.reset_data();
    result3_.reset_data();
    result4_.reset_data();
    result5_.reset_data();
    result6_.reset_data();
    result7_.reset_data();
  }

  void compiled_args(CompiledNodeArgs& args) override;
  variable_list apply_with_saved(const variable_list& inputs, SwapSavedVariables& saved) override;
  int64_t attn_dim_per_head = 0;
  int64_t attn_head_num = 0;
  double dropout_prob;
  SavedVariable key_;
  SavedVariable key_bias_;
  SavedVariable key_weight_;
  SavedVariable out_proj_bias_;
  SavedVariable out_proj_weight_;
  SavedVariable query_;
  SavedVariable query_bias_;
  SavedVariable query_weight_;
  bool softmax_use_float;
  int64_t src_len = 0;
  int64_t tgt_len = 0;
  SavedVariable value_;
  SavedVariable value_bias_;
  SavedVariable value_weight_;
  SavedVariable result1_;
  SavedVariable result2_;
  SavedVariable result3_;
  SavedVariable result4_;
  SavedVariable result5_;
  SavedVariable result6_;
  SavedVariable result7_;

};
#ifdef _WIN32
struct NpuFusionAttentionBackward0 : public TraceableFunction {
  TORCH_API NpuFusionAttentionBackward0() = default;
#else
struct TORCH_API NpuFusionAttentionBackward0 : public TraceableFunction {
#endif
  using TraceableFunction::TraceableFunction;
  variable_list apply(variable_list&& grads) override;
  std::string name() const override { return "NpuFusionAttentionBackward0"; }
  void release_variables() override {
    std::lock_guard<std::mutex> lock(mutex_);
    atten_mask_.reset_data();
    key_.reset_data();
    padding_mask_.reset_data();
    pse_.reset_data();
    query_.reset_data();
    value_.reset_data();
    result0_.reset_data();
    result1_.reset_data();
    result2_.reset_data();
    result3_.reset_data();
  }

  void compiled_args(CompiledNodeArgs& args) override;
  variable_list apply_with_saved(const variable_list& inputs, SwapSavedVariables& saved) override;
  c10::OptionalArray<int64_t> actual_seq_kvlen;
  c10::OptionalArray<int64_t> actual_seq_qlen;
  SavedVariable atten_mask_;
  bool gen_mask_parallel;
  int64_t head_num = 0;
  int64_t inner_precise = 0;
  std::string input_layout;
  double keep_prob;
  SavedVariable key_;
  int64_t next_tockens = 0;
  SavedVariable padding_mask_;
  int64_t pre_tockens = 0;
  c10::OptionalArray<int64_t> prefix;
  SavedVariable pse_;
  SavedVariable query_;
  double scale;
  int64_t sparse_mode = 0;
  bool sync;
  SavedVariable value_;
  SavedVariable result0_;
  SavedVariable result1_;
  SavedVariable result2_;
  SavedVariable result3_;
  int64_t result4 = 0;
  int64_t result5 = 0;
  int64_t result6 = 0;

};
#ifdef _WIN32
struct NpuFusionAttentionV3Backward0 : public TraceableFunction {
  TORCH_API NpuFusionAttentionV3Backward0() = default;
#else
struct TORCH_API NpuFusionAttentionV3Backward0 : public TraceableFunction {
#endif
  using TraceableFunction::TraceableFunction;
  variable_list apply(variable_list&& grads) override;
  std::string name() const override { return "NpuFusionAttentionV3Backward0"; }
  void release_variables() override {
    std::lock_guard<std::mutex> lock(mutex_);
    atten_mask_.reset_data();
    bias_.reset_data();
    pse_.reset_data();
    weight_.reset_data();
    x_.reset_data();
    result0_.reset_data();
    result1_.reset_data();
    result2_.reset_data();
    result3_.reset_data();
  }

  void compiled_args(CompiledNodeArgs& args) override;
  variable_list apply_with_saved(const variable_list& inputs, SwapSavedVariables& saved) override;
  SavedVariable atten_mask_;
  SavedVariable bias_;
  bool gen_mask_parallel;
  int64_t head_num = 0;
  int64_t head_size = 0;
  std::string input_layout;
  double keep_prob;
  int64_t next_tockens = 0;
  int64_t pre_tockens = 0;
  c10::OptionalArray<int64_t> prefix;
  SavedVariable pse_;
  int64_t pse_type = 0;
  double scale_k;
  double scale_q;
  double scale_qk;
  int64_t sparse_mode = 0;
  bool sync;
  SavedVariable weight_;
  SavedVariable x_;
  SavedVariable result0_;
  SavedVariable result1_;
  SavedVariable result2_;
  SavedVariable result3_;
  int64_t result4 = 0;
  int64_t result5 = 0;
  int64_t result6 = 0;

};
#ifdef _WIN32
struct NpuGruBackward0 : public TraceableFunction {
  TORCH_API NpuGruBackward0() = default;
#else
struct TORCH_API NpuGruBackward0 : public TraceableFunction {
#endif
  using TraceableFunction::TraceableFunction;
  variable_list apply(variable_list&& grads) override;
  std::string name() const override { return "NpuGruBackward0"; }
  void release_variables() override {
    std::lock_guard<std::mutex> lock(mutex_);
    bias_hidden_.reset_data();
    bias_input_.reset_data();
    hx_.reset_data();
    input_.reset_data();
    seq_length_.reset_data();
    weight_hidden_.reset_data();
    weight_input_.reset_data();
    result0_.reset_data();
    result1_.reset_data();
    result2_.reset_data();
    result3_.reset_data();
    result4_.reset_data();
    result5_.reset_data();
  }

  void compiled_args(CompiledNodeArgs& args) override;
  variable_list apply_with_saved(const variable_list& inputs, SwapSavedVariables& saved) override;
  SavedVariable bias_hidden_;
  SavedVariable bias_input_;
  SavedVariable hx_;
  SavedVariable input_;
  SavedVariable seq_length_;
  SavedVariable weight_hidden_;
  SavedVariable weight_input_;
  SavedVariable result0_;
  SavedVariable result1_;
  SavedVariable result2_;
  SavedVariable result3_;
  SavedVariable result4_;
  SavedVariable result5_;

};
#ifdef _WIN32
struct NpuGegluBackward0 : public TraceableFunction {
  TORCH_API NpuGegluBackward0() = default;
#else
struct TORCH_API NpuGegluBackward0 : public TraceableFunction {
#endif
  using TraceableFunction::TraceableFunction;
  variable_list apply(variable_list&& grads) override;
  std::string name() const override { return "NpuGegluBackward0"; }
  void release_variables() override {
    std::lock_guard<std::mutex> lock(mutex_);
    self_.reset_data();
    result1_.reset_data();
  }

  void compiled_args(CompiledNodeArgs& args) override;
  variable_list apply_with_saved(const variable_list& inputs, SwapSavedVariables& saved) override;
  bool activate_left;
  int64_t approximate = 0;
  int64_t dim = 0;
  SavedVariable self_;
  SavedVariable result1_;

};
#ifdef _WIN32
struct NpuLstmBackward0 : public TraceableFunction {
  TORCH_API NpuLstmBackward0() = default;
#else
struct TORCH_API NpuLstmBackward0 : public TraceableFunction {
#endif
  using TraceableFunction::TraceableFunction;
  variable_list apply(variable_list&& grads) override;
  std::string name() const override { return "NpuLstmBackward0"; }
  void release_variables() override {
    std::lock_guard<std::mutex> lock(mutex_);
    bias_.reset_data();
    c_.reset_data();
    h_.reset_data();
    input_.reset_data();
    weight_.reset_data();
    result0_.reset_data();
    result1_.reset_data();
    result2_.reset_data();
    result3_.reset_data();
    result4_.reset_data();
    result5_.reset_data();
    result6_.reset_data();
    result7_.reset_data();
  }

  void compiled_args(CompiledNodeArgs& args) override;
  variable_list apply_with_saved(const variable_list& inputs, SwapSavedVariables& saved) override;
  SavedVariable bias_;
  SavedVariable c_;
  SavedVariable h_;
  SavedVariable input_;
  SavedVariable weight_;
  SavedVariable result0_;
  SavedVariable result1_;
  SavedVariable result2_;
  SavedVariable result3_;
  SavedVariable result4_;
  SavedVariable result5_;
  SavedVariable result6_;
  SavedVariable result7_;

};
#ifdef _WIN32
struct NpuLstmDataBackward0 : public TraceableFunction {
  TORCH_API NpuLstmDataBackward0() = default;
#else
struct TORCH_API NpuLstmDataBackward0 : public TraceableFunction {
#endif
  using TraceableFunction::TraceableFunction;
  variable_list apply(variable_list&& grads) override;
  std::string name() const override { return "NpuLstmDataBackward0"; }
  void release_variables() override {
    std::lock_guard<std::mutex> lock(mutex_);
    batch_sizes_.reset_data();
    bias_.reset_data();
    c_.reset_data();
    h_.reset_data();
    input_.reset_data();
    weight_.reset_data();
    result0_.reset_data();
    result1_.reset_data();
    result2_.reset_data();
    result3_.reset_data();
    result4_.reset_data();
    result5_.reset_data();
    result6_.reset_data();
    result7_.reset_data();
  }

  void compiled_args(CompiledNodeArgs& args) override;
  variable_list apply_with_saved(const variable_list& inputs, SwapSavedVariables& saved) override;
  SavedVariable batch_sizes_;
  SavedVariable bias_;
  SavedVariable c_;
  bool direction;
  SavedVariable h_;
  SavedVariable input_;
  SavedVariable weight_;
  SavedVariable result0_;
  SavedVariable result1_;
  SavedVariable result2_;
  SavedVariable result3_;
  SavedVariable result4_;
  SavedVariable result5_;
  SavedVariable result6_;
  SavedVariable result7_;

};
#ifdef _WIN32
struct NpuLstmCellBackward0 : public TraceableFunction {
  TORCH_API NpuLstmCellBackward0() = default;
#else
struct TORCH_API NpuLstmCellBackward0 : public TraceableFunction {
#endif
  using TraceableFunction::TraceableFunction;
  variable_list apply(variable_list&& grads) override;
  std::string name() const override { return "NpuLstmCellBackward0"; }
  void release_variables() override {
    std::lock_guard<std::mutex> lock(mutex_);
    c_.reset_data();
    h_.reset_data();
    input_.reset_data();
    w_hh_.reset_data();
    w_ih_.reset_data();
    result0_.reset_data();
    result1_.reset_data();
    result2_.reset_data();
    result3_.reset_data();
    result4_.reset_data();
    result5_.reset_data();
    result6_.reset_data();
    result7_.reset_data();
  }

  void compiled_args(CompiledNodeArgs& args) override;
  variable_list apply_with_saved(const variable_list& inputs, SwapSavedVariables& saved) override;
  SavedVariable c_;
  SavedVariable h_;
  SavedVariable input_;
  SavedVariable w_hh_;
  SavedVariable w_ih_;
  SavedVariable result0_;
  SavedVariable result1_;
  SavedVariable result2_;
  SavedVariable result3_;
  SavedVariable result4_;
  SavedVariable result5_;
  SavedVariable result6_;
  SavedVariable result7_;

};
#ifdef _WIN32
struct DropoutWithByteMaskBackward0 : public TraceableFunction {
  TORCH_API DropoutWithByteMaskBackward0() = default;
#else
struct TORCH_API DropoutWithByteMaskBackward0 : public TraceableFunction {
#endif
  using TraceableFunction::TraceableFunction;
  variable_list apply(variable_list&& grads) override;
  std::string name() const override { return "DropoutWithByteMaskBackward0"; }
  void release_variables() override {
    std::lock_guard<std::mutex> lock(mutex_);
    result1_.reset_data();
  }

  void compiled_args(CompiledNodeArgs& args) override;
  variable_list apply_with_saved(const variable_list& inputs, SwapSavedVariables& saved) override;
  double p;
  SavedVariable result1_;

};
#ifdef _WIN32
struct NpuDropoutBackward0 : public TraceableFunction {
  TORCH_API NpuDropoutBackward0() = default;
#else
struct TORCH_API NpuDropoutBackward0 : public TraceableFunction {
#endif
  using TraceableFunction::TraceableFunction;
  variable_list apply(variable_list&& grads) override;
  std::string name() const override { return "NpuDropoutBackward0"; }
  void release_variables() override {
    std::lock_guard<std::mutex> lock(mutex_);
    result1_.reset_data();
  }

  void compiled_args(CompiledNodeArgs& args) override;
  variable_list apply_with_saved(const variable_list& inputs, SwapSavedVariables& saved) override;
  double p;
  SavedVariable result1_;

};
#ifdef _WIN32
struct NpuDropoutDoMaskBackward0 : public TraceableFunction {
  TORCH_API NpuDropoutDoMaskBackward0() = default;
#else
struct TORCH_API NpuDropoutDoMaskBackward0 : public TraceableFunction {
#endif
  using TraceableFunction::TraceableFunction;
  variable_list apply(variable_list&& grads) override;
  std::string name() const override { return "NpuDropoutDoMaskBackward0"; }
  void release_variables() override {
    std::lock_guard<std::mutex> lock(mutex_);
    result1_.reset_data();
  }

  void compiled_args(CompiledNodeArgs& args) override;
  variable_list apply_with_saved(const variable_list& inputs, SwapSavedVariables& saved) override;
  double p;
  SavedVariable result1_;

};
#ifdef _WIN32
struct NpuCiouBackward0 : public TraceableFunction {
  TORCH_API NpuCiouBackward0() = default;
#else
struct TORCH_API NpuCiouBackward0 : public TraceableFunction {
#endif
  using TraceableFunction::TraceableFunction;
  variable_list apply(variable_list&& grads) override;
  std::string name() const override { return "NpuCiouBackward0"; }
  void release_variables() override {
    std::lock_guard<std::mutex> lock(mutex_);
    gtboxes_.reset_data();
    self_.reset_data();
    result1_.reset_data();
  }

  void compiled_args(CompiledNodeArgs& args) override;
  variable_list apply_with_saved(const variable_list& inputs, SwapSavedVariables& saved) override;
  SavedVariable gtboxes_;
  bool is_cross;
  int64_t mode = 0;
  SavedVariable self_;
  bool trans;
  SavedVariable result1_;

};
#ifdef _WIN32
struct NpuFusedAttentionScoreFwdBackward0 : public TraceableFunction {
  TORCH_API NpuFusedAttentionScoreFwdBackward0() = default;
#else
struct TORCH_API NpuFusedAttentionScoreFwdBackward0 : public TraceableFunction {
#endif
  using TraceableFunction::TraceableFunction;
  variable_list apply(variable_list&& grads) override;
  std::string name() const override { return "NpuFusedAttentionScoreFwdBackward0"; }
  void release_variables() override {
    std::lock_guard<std::mutex> lock(mutex_);
    key_layer_.reset_data();
    query_layer_.reset_data();
    value_layer_.reset_data();
    result1_.reset_data();
    result2_.reset_data();
  }

  void compiled_args(CompiledNodeArgs& args) override;
  variable_list apply_with_saved(const variable_list& inputs, SwapSavedVariables& saved) override;
  bool dx_transpose;
  double keep_prob;
  SavedVariable key_layer_;
  bool key_transpose;
  SavedVariable query_layer_;
  bool query_transpose;
  at::Scalar scale;
  SavedVariable value_layer_;
  bool value_transpose;
  SavedVariable result1_;
  SavedVariable result2_;

};
#ifdef _WIN32
struct NpuBmmv2Backward0 : public TraceableFunction {
  TORCH_API NpuBmmv2Backward0() = default;
#else
struct TORCH_API NpuBmmv2Backward0 : public TraceableFunction {
#endif
  using TraceableFunction::TraceableFunction;
  variable_list apply(variable_list&& grads) override;
  std::string name() const override { return "NpuBmmv2Backward0"; }
  void release_variables() override {
    std::lock_guard<std::mutex> lock(mutex_);
    mat2_.reset_data();
    self_.reset_data();
  }

  void compiled_args(CompiledNodeArgs& args) override;
  variable_list apply_with_saved(const variable_list& inputs, SwapSavedVariables& saved) override;
  SavedVariable mat2_;
  std::vector<c10::SymInt> mat2_sym_sizes;
  SavedVariable self_;
  std::vector<c10::SymInt> self_sym_sizes;

};
#ifdef _WIN32
struct NpuMaxBackward0 : public TraceableFunction {
  TORCH_API NpuMaxBackward0() = default;
#else
struct TORCH_API NpuMaxBackward0 : public TraceableFunction {
#endif
  using TraceableFunction::TraceableFunction;
  variable_list apply(variable_list&& grads) override;
  std::string name() const override { return "NpuMaxBackward0"; }
  void release_variables() override {
    std::lock_guard<std::mutex> lock(mutex_);
    indices_.reset_data();
  }

  void compiled_args(CompiledNodeArgs& args) override;
  variable_list apply_with_saved(const variable_list& inputs, SwapSavedVariables& saved) override;
  int64_t dim = 0;
  bool keepdim;
  std::vector<c10::SymInt> self_sym_sizes;
  SavedVariable indices_;

};
#ifdef _WIN32
struct NpuMinBackward0 : public TraceableFunction {
  TORCH_API NpuMinBackward0() = default;
#else
struct TORCH_API NpuMinBackward0 : public TraceableFunction {
#endif
  using TraceableFunction::TraceableFunction;
  variable_list apply(variable_list&& grads) override;
  std::string name() const override { return "NpuMinBackward0"; }
  void release_variables() override {
    std::lock_guard<std::mutex> lock(mutex_);
    indices_.reset_data();
  }

  void compiled_args(CompiledNodeArgs& args) override;
  variable_list apply_with_saved(const variable_list& inputs, SwapSavedVariables& saved) override;
  int64_t dim = 0;
  bool keepdim;
  std::vector<c10::SymInt> self_sym_sizes;
  SavedVariable indices_;

};
#ifdef _WIN32
struct NpuPsRoiPoolingBackward0 : public TraceableFunction {
  TORCH_API NpuPsRoiPoolingBackward0() = default;
#else
struct TORCH_API NpuPsRoiPoolingBackward0 : public TraceableFunction {
#endif
  using TraceableFunction::TraceableFunction;
  variable_list apply(variable_list&& grads) override;
  std::string name() const override { return "NpuPsRoiPoolingBackward0"; }
  void release_variables() override {
    std::lock_guard<std::mutex> lock(mutex_);
    rois_.reset_data();
  }

  void compiled_args(CompiledNodeArgs& args) override;
  variable_list apply_with_saved(const variable_list& inputs, SwapSavedVariables& saved) override;
  int64_t group_size = 0;
  int64_t output_dim = 0;
  SavedVariable rois_;
  c10::SymInt self_sym_argsize_2;
  c10::SymInt self_sym_argsize_3;
  double spatial_scale;

};
#ifdef _WIN32
struct NpuConfusionTransposeBackward0 : public TraceableFunction {
  TORCH_API NpuConfusionTransposeBackward0() = default;
#else
struct TORCH_API NpuConfusionTransposeBackward0 : public TraceableFunction {
#endif
  using TraceableFunction::TraceableFunction;
  variable_list apply(variable_list&& grads) override;
  std::string name() const override { return "NpuConfusionTransposeBackward0"; }
  void release_variables() override {


  }

  void compiled_args(CompiledNodeArgs& args) override;
  variable_list apply_with_saved(const variable_list& inputs, SwapSavedVariables& saved) override;
  std::vector<int64_t> perm;
  std::vector<c10::SymInt> self_sym_sizes;
  bool transpose_first;

};
#ifdef _WIN32
struct SeluBackward0 : public TraceableFunction {
  TORCH_API SeluBackward0() = default;
#else
struct TORCH_API SeluBackward0 : public TraceableFunction {
#endif
  using TraceableFunction::TraceableFunction;
  variable_list apply(variable_list&& grads) override;
  std::string name() const override { return "SeluBackward0"; }
  void release_variables() override {
    std::lock_guard<std::mutex> lock(mutex_);
    result_.reset_data();
  }

  void compiled_args(CompiledNodeArgs& args) override;
  variable_list apply_with_saved(const variable_list& inputs, SwapSavedVariables& saved) override;
  SavedVariable result_;

};
#ifdef _WIN32
struct NpuSiluBackward0 : public TraceableFunction {
  TORCH_API NpuSiluBackward0() = default;
#else
struct TORCH_API NpuSiluBackward0 : public TraceableFunction {
#endif
  using TraceableFunction::TraceableFunction;
  variable_list apply(variable_list&& grads) override;
  std::string name() const override { return "NpuSiluBackward0"; }
  void release_variables() override {
    std::lock_guard<std::mutex> lock(mutex_);
    self_.reset_data();
    result_.reset_data();
  }

  void compiled_args(CompiledNodeArgs& args) override;
  variable_list apply_with_saved(const variable_list& inputs, SwapSavedVariables& saved) override;
  SavedVariable self_;
  SavedVariable result_;

};
#ifdef _WIN32
struct FastGeluBackward0 : public TraceableFunction {
  TORCH_API FastGeluBackward0() = default;
#else
struct TORCH_API FastGeluBackward0 : public TraceableFunction {
#endif
  using TraceableFunction::TraceableFunction;
  variable_list apply(variable_list&& grads) override;
  std::string name() const override { return "FastGeluBackward0"; }
  void release_variables() override {
    std::lock_guard<std::mutex> lock(mutex_);
    self_.reset_data();
  }

  void compiled_args(CompiledNodeArgs& args) override;
  variable_list apply_with_saved(const variable_list& inputs, SwapSavedVariables& saved) override;
  SavedVariable self_;

};
#ifdef _WIN32
struct NpuRotaryMulBackward0 : public TraceableFunction {
  TORCH_API NpuRotaryMulBackward0() = default;
#else
struct TORCH_API NpuRotaryMulBackward0 : public TraceableFunction {
#endif
  using TraceableFunction::TraceableFunction;
  variable_list apply(variable_list&& grads) override;
  std::string name() const override { return "NpuRotaryMulBackward0"; }
  void release_variables() override {
    std::lock_guard<std::mutex> lock(mutex_);
    r1_.reset_data();
    r2_.reset_data();
    self_.reset_data();
  }

  void compiled_args(CompiledNodeArgs& args) override;
  variable_list apply_with_saved(const variable_list& inputs, SwapSavedVariables& saved) override;
  SavedVariable r1_;
  SavedVariable r2_;
  SavedVariable self_;

};
#ifdef _WIN32
struct NpuDiouBackward0 : public TraceableFunction {
  TORCH_API NpuDiouBackward0() = default;
#else
struct TORCH_API NpuDiouBackward0 : public TraceableFunction {
#endif
  using TraceableFunction::TraceableFunction;
  variable_list apply(variable_list&& grads) override;
  std::string name() const override { return "NpuDiouBackward0"; }
  void release_variables() override {
    std::lock_guard<std::mutex> lock(mutex_);
    gtboxes_.reset_data();
    self_.reset_data();
  }

  void compiled_args(CompiledNodeArgs& args) override;
  variable_list apply_with_saved(const variable_list& inputs, SwapSavedVariables& saved) override;
  SavedVariable gtboxes_;
  bool is_cross;
  int64_t mode = 0;
  SavedVariable self_;
  bool trans;

};
#ifdef _WIN32
struct NpuGiouBackward0 : public TraceableFunction {
  TORCH_API NpuGiouBackward0() = default;
#else
struct TORCH_API NpuGiouBackward0 : public TraceableFunction {
#endif
  using TraceableFunction::TraceableFunction;
  variable_list apply(variable_list&& grads) override;
  std::string name() const override { return "NpuGiouBackward0"; }
  void release_variables() override {
    std::lock_guard<std::mutex> lock(mutex_);
    gtboxes_.reset_data();
    self_.reset_data();
  }

  void compiled_args(CompiledNodeArgs& args) override;
  variable_list apply_with_saved(const variable_list& inputs, SwapSavedVariables& saved) override;
  SavedVariable gtboxes_;
  bool is_cross;
  int64_t mode = 0;
  SavedVariable self_;
  bool trans;

};
#ifdef _WIN32
struct NpuMishBackward0 : public TraceableFunction {
  TORCH_API NpuMishBackward0() = default;
#else
struct TORCH_API NpuMishBackward0 : public TraceableFunction {
#endif
  using TraceableFunction::TraceableFunction;
  variable_list apply(variable_list&& grads) override;
  std::string name() const override { return "NpuMishBackward0"; }
  void release_variables() override {
    std::lock_guard<std::mutex> lock(mutex_);
    self_.reset_data();
  }

  void compiled_args(CompiledNodeArgs& args) override;
  variable_list apply_with_saved(const variable_list& inputs, SwapSavedVariables& saved) override;
  SavedVariable self_;

};
#ifdef _WIN32
struct NpuSoftmaxCrossEntropyWithLogitsBackward0 : public TraceableFunction {
  TORCH_API NpuSoftmaxCrossEntropyWithLogitsBackward0() = default;
#else
struct TORCH_API NpuSoftmaxCrossEntropyWithLogitsBackward0 : public TraceableFunction {
#endif
  using TraceableFunction::TraceableFunction;
  variable_list apply(variable_list&& grads) override;
  std::string name() const override { return "NpuSoftmaxCrossEntropyWithLogitsBackward0"; }
  void release_variables() override {
    std::lock_guard<std::mutex> lock(mutex_);
    labels_.reset_data();
    self_.reset_data();
  }

  void compiled_args(CompiledNodeArgs& args) override;
  variable_list apply_with_saved(const variable_list& inputs, SwapSavedVariables& saved) override;
  SavedVariable labels_;
  SavedVariable self_;

};
#ifdef _WIN32
struct NpuLinearBackward0 : public TraceableFunction {
  TORCH_API NpuLinearBackward0() = default;
#else
struct TORCH_API NpuLinearBackward0 : public TraceableFunction {
#endif
  using TraceableFunction::TraceableFunction;
  variable_list apply(variable_list&& grads) override;
  std::string name() const override { return "NpuLinearBackward0"; }
  void release_variables() override {
    std::lock_guard<std::mutex> lock(mutex_);
    input_.reset_data();
    weight_.reset_data();
  }

  void compiled_args(CompiledNodeArgs& args) override;
  variable_list apply_with_saved(const variable_list& inputs, SwapSavedVariables& saved) override;
  SavedVariable input_;
  SavedVariable weight_;

};
#ifdef _WIN32
struct NpuDropoutWithAddSoftmaxBackward0 : public TraceableFunction {
  TORCH_API NpuDropoutWithAddSoftmaxBackward0() = default;
#else
struct TORCH_API NpuDropoutWithAddSoftmaxBackward0 : public TraceableFunction {
#endif
  using TraceableFunction::TraceableFunction;
  variable_list apply(variable_list&& grads) override;
  std::string name() const override { return "NpuDropoutWithAddSoftmaxBackward0"; }
  void release_variables() override {
    std::lock_guard<std::mutex> lock(mutex_);
    result0_.reset_data();
    result1_.reset_data();
  }

  void compiled_args(CompiledNodeArgs& args) override;
  variable_list apply_with_saved(const variable_list& inputs, SwapSavedVariables& saved) override;
  at::Scalar alpha;
  int64_t dim = 0;
  double prob;
  SavedVariable result0_;
  SavedVariable result1_;

};
#ifdef _WIN32
struct NpuDtypeCastBackward0 : public TraceableFunction {
  TORCH_API NpuDtypeCastBackward0() = default;
#else
struct TORCH_API NpuDtypeCastBackward0 : public TraceableFunction {
#endif
  using TraceableFunction::TraceableFunction;
  variable_list apply(variable_list&& grads) override;
  std::string name() const override { return "NpuDtypeCastBackward0"; }
  void release_variables() override {


  }

  void compiled_args(CompiledNodeArgs& args) override;
  variable_list apply_with_saved(const variable_list& inputs, SwapSavedVariables& saved) override;
  at::ScalarType self_scalar_type;

};
#ifdef _WIN32
struct NpuConvolutionTransposeBackward0 : public TraceableFunction {
  TORCH_API NpuConvolutionTransposeBackward0() = default;
#else
struct TORCH_API NpuConvolutionTransposeBackward0 : public TraceableFunction {
#endif
  using TraceableFunction::TraceableFunction;
  variable_list apply(variable_list&& grads) override;
  std::string name() const override { return "NpuConvolutionTransposeBackward0"; }
  void release_variables() override {
    std::lock_guard<std::mutex> lock(mutex_);
    input_.reset_data();
    weight_.reset_data();
  }

  void compiled_args(CompiledNodeArgs& args) override;
  variable_list apply_with_saved(const variable_list& inputs, SwapSavedVariables& saved) override;
  std::vector<int64_t> dilation;
  int64_t groups = 0;
  SavedVariable input_;
  std::vector<int64_t> output_padding;
  std::vector<int64_t> padding;
  std::vector<int64_t> stride;
  SavedVariable weight_;

};
#ifdef _WIN32
struct NpuConvolutionBackward0 : public TraceableFunction {
  TORCH_API NpuConvolutionBackward0() = default;
#else
struct TORCH_API NpuConvolutionBackward0 : public TraceableFunction {
#endif
  using TraceableFunction::TraceableFunction;
  variable_list apply(variable_list&& grads) override;
  std::string name() const override { return "NpuConvolutionBackward0"; }
  void release_variables() override {
    std::lock_guard<std::mutex> lock(mutex_);
    input_.reset_data();
    weight_.reset_data();
  }

  void compiled_args(CompiledNodeArgs& args) override;
  variable_list apply_with_saved(const variable_list& inputs, SwapSavedVariables& saved) override;
  std::vector<int64_t> dilation;
  int64_t groups = 0;
  SavedVariable input_;
  std::vector<int64_t> padding;
  std::vector<int64_t> stride;
  SavedVariable weight_;

};
#ifdef _WIN32
struct NpuDeformableConv2DBackward0 : public TraceableFunction {
  TORCH_API NpuDeformableConv2DBackward0() = default;
#else
struct TORCH_API NpuDeformableConv2DBackward0 : public TraceableFunction {
#endif
  using TraceableFunction::TraceableFunction;
  variable_list apply(variable_list&& grads) override;
  std::string name() const override { return "NpuDeformableConv2DBackward0"; }
  void release_variables() override {
    std::lock_guard<std::mutex> lock(mutex_);
    input_.reset_data();
    offset_.reset_data();
    weight_.reset_data();
    result1_.reset_data();
  }

  void compiled_args(CompiledNodeArgs& args) override;
  variable_list apply_with_saved(const variable_list& inputs, SwapSavedVariables& saved) override;
  int64_t deformable_groups = 0;
  std::vector<int64_t> dilation;
  int64_t groups = 0;
  SavedVariable input_;
  std::vector<int64_t> kernel_size;
  bool modulated;
  SavedVariable offset_;
  std::vector<int64_t> padding;
  std::vector<int64_t> stride;
  SavedVariable weight_;
  SavedVariable result1_;

};
#ifdef _WIN32
struct NpuScaledMaskedSoftmaxBackward0 : public TraceableFunction {
  TORCH_API NpuScaledMaskedSoftmaxBackward0() = default;
#else
struct TORCH_API NpuScaledMaskedSoftmaxBackward0 : public TraceableFunction {
#endif
  using TraceableFunction::TraceableFunction;
  variable_list apply(variable_list&& grads) override;
  std::string name() const override { return "NpuScaledMaskedSoftmaxBackward0"; }
  void release_variables() override {
    std::lock_guard<std::mutex> lock(mutex_);
    mask_.reset_data();
    result_.reset_data();
  }

  void compiled_args(CompiledNodeArgs& args) override;
  variable_list apply_with_saved(const variable_list& inputs, SwapSavedVariables& saved) override;
  bool fixed_triu_mask;
  SavedVariable mask_;
  at::Scalar scale;
  SavedVariable result_;

};
#ifdef _WIN32
struct BinaryCrossEntropyWithLogitsBackward0 : public TraceableFunction {
  TORCH_API BinaryCrossEntropyWithLogitsBackward0() = default;
#else
struct TORCH_API BinaryCrossEntropyWithLogitsBackward0 : public TraceableFunction {
#endif
  using TraceableFunction::TraceableFunction;
  variable_list apply(variable_list&& grads) override;
  std::string name() const override { return "BinaryCrossEntropyWithLogitsBackward0"; }
  void release_variables() override {
    std::lock_guard<std::mutex> lock(mutex_);
    pos_weight_.reset_data();
    self_.reset_data();
    target_.reset_data();
    weight_.reset_data();
  }

  void compiled_args(CompiledNodeArgs& args) override;
  variable_list apply_with_saved(const variable_list& inputs, SwapSavedVariables& saved) override;
  SavedVariable pos_weight_;
  int64_t reduction = 0;
  SavedVariable self_;
  SavedVariable target_;
  SavedVariable weight_;

};
#ifdef _WIN32
struct KlDivBackward0 : public TraceableFunction {
  TORCH_API KlDivBackward0() = default;
#else
struct TORCH_API KlDivBackward0 : public TraceableFunction {
#endif
  using TraceableFunction::TraceableFunction;
  variable_list apply(variable_list&& grads) override;
  std::string name() const override { return "KlDivBackward0"; }
  void release_variables() override {
    std::lock_guard<std::mutex> lock(mutex_);
    self_.reset_data();
    target_.reset_data();
  }

  void compiled_args(CompiledNodeArgs& args) override;
  variable_list apply_with_saved(const variable_list& inputs, SwapSavedVariables& saved) override;
  bool log_target;
  int64_t reduction = 0;
  SavedVariable self_;
  SavedVariable target_;

};
#ifdef _WIN32
struct L1LossBackward0 : public TraceableFunction {
  TORCH_API L1LossBackward0() = default;
#else
struct TORCH_API L1LossBackward0 : public TraceableFunction {
#endif
  using TraceableFunction::TraceableFunction;
  variable_list apply(variable_list&& grads) override;
  std::string name() const override { return "L1LossBackward0"; }
  void release_variables() override {
    std::lock_guard<std::mutex> lock(mutex_);
    self_.reset_data();
    target_.reset_data();
  }

  void compiled_args(CompiledNodeArgs& args) override;
  variable_list apply_with_saved(const variable_list& inputs, SwapSavedVariables& saved) override;
  int64_t reduction = 0;
  SavedVariable self_;
  SavedVariable target_;

};
#ifdef _WIN32
struct NpuRmsNormBackward0 : public TraceableFunction {
  TORCH_API NpuRmsNormBackward0() = default;
#else
struct TORCH_API NpuRmsNormBackward0 : public TraceableFunction {
#endif
  using TraceableFunction::TraceableFunction;
  variable_list apply(variable_list&& grads) override;
  std::string name() const override { return "NpuRmsNormBackward0"; }
  void release_variables() override {
    std::lock_guard<std::mutex> lock(mutex_);
    gamma_.reset_data();
    self_.reset_data();
    result1_.reset_data();
  }

  void compiled_args(CompiledNodeArgs& args) override;
  variable_list apply_with_saved(const variable_list& inputs, SwapSavedVariables& saved) override;
  SavedVariable gamma_;
  SavedVariable self_;
  SavedVariable result1_;

};
#ifdef _WIN32
struct NpuSwigluBackward0 : public TraceableFunction {
  TORCH_API NpuSwigluBackward0() = default;
#else
struct TORCH_API NpuSwigluBackward0 : public TraceableFunction {
#endif
  using TraceableFunction::TraceableFunction;
  variable_list apply(variable_list&& grads) override;
  std::string name() const override { return "NpuSwigluBackward0"; }
  void release_variables() override {
    std::lock_guard<std::mutex> lock(mutex_);
    self_.reset_data();
  }

  void compiled_args(CompiledNodeArgs& args) override;
  variable_list apply_with_saved(const variable_list& inputs, SwapSavedVariables& saved) override;
  int64_t dim = 0;
  SavedVariable self_;

};
#ifdef _WIN32
struct NpuAddLayerNormBackward0 : public TraceableFunction {
  TORCH_API NpuAddLayerNormBackward0() = default;
#else
struct TORCH_API NpuAddLayerNormBackward0 : public TraceableFunction {
#endif
  using TraceableFunction::TraceableFunction;
  variable_list apply(variable_list&& grads) override;
  std::string name() const override { return "NpuAddLayerNormBackward0"; }
  void release_variables() override {
    std::lock_guard<std::mutex> lock(mutex_);
    gamma_.reset_data();
    x1_.reset_data();
    x2_.reset_data();
    result1_.reset_data();
    result2_.reset_data();
  }

  void compiled_args(CompiledNodeArgs& args) override;
  variable_list apply_with_saved(const variable_list& inputs, SwapSavedVariables& saved) override;
  SavedVariable gamma_;
  SavedVariable x1_;
  SavedVariable x2_;
  SavedVariable result1_;
  SavedVariable result2_;

};
#ifdef _WIN32
struct NpuDeepNormBackward0 : public TraceableFunction {
  TORCH_API NpuDeepNormBackward0() = default;
#else
struct TORCH_API NpuDeepNormBackward0 : public TraceableFunction {
#endif
  using TraceableFunction::TraceableFunction;
  variable_list apply(variable_list&& grads) override;
  std::string name() const override { return "NpuDeepNormBackward0"; }
  void release_variables() override {
    std::lock_guard<std::mutex> lock(mutex_);
    gamma_.reset_data();
    gx_.reset_data();
    x_.reset_data();
    result0_.reset_data();
    result1_.reset_data();
  }

  void compiled_args(CompiledNodeArgs& args) override;
  variable_list apply_with_saved(const variable_list& inputs, SwapSavedVariables& saved) override;
  double alpha;
  SavedVariable gamma_;
  SavedVariable gx_;
  SavedVariable x_;
  SavedVariable result0_;
  SavedVariable result1_;

};
#ifdef _WIN32
struct NpuFormatCastBackward0 : public TraceableFunction {
  TORCH_API NpuFormatCastBackward0() = default;
#else
struct TORCH_API NpuFormatCastBackward0 : public TraceableFunction {
#endif
  using TraceableFunction::TraceableFunction;
  variable_list apply(variable_list&& grads) override;
  std::string name() const override { return "NpuFormatCastBackward0"; }
  void release_variables() override {


  }

  void compiled_args(CompiledNodeArgs& args) override;
  variable_list apply_with_saved(const variable_list& inputs, SwapSavedVariables& saved) override;


};
#ifdef _WIN32
struct NpuMultiHeadAttentionV2Backward0 : public TraceableFunction {
  TORCH_API NpuMultiHeadAttentionV2Backward0() = default;
#else
struct TORCH_API NpuMultiHeadAttentionV2Backward0 : public TraceableFunction {
#endif
  using TraceableFunction::TraceableFunction;
  variable_list apply(variable_list&& grads) override;
  std::string name() const override { return "NpuMultiHeadAttentionV2Backward0"; }
  void release_variables() override {
    std::lock_guard<std::mutex> lock(mutex_);
    alibi_mask_.reset_data();
    atten_mask_.reset_data();
    key_.reset_data();
    query_.reset_data();
    value_.reset_data();
    result0_.reset_data();
    result1_.reset_data();
  }

  void compiled_args(CompiledNodeArgs& args) override;
  variable_list apply_with_saved(const variable_list& inputs, SwapSavedVariables& saved) override;
  SavedVariable alibi_mask_;
  SavedVariable atten_mask_;
  bool gen_mask_parallel;
  int64_t head_num = 0;
  std::string input_layout;
  double keep_prob;
  SavedVariable key_;
  int64_t next_tokens = 0;
  int64_t pre_tokens = 0;
  SavedVariable query_;
  double scale;
  bool sync;
  SavedVariable value_;
  SavedVariable result0_;
  SavedVariable result1_;
  int64_t result2 = 0;
  int64_t result3 = 0;
  int64_t result4 = 0;

};

}}} // namespace at_npu::autograd::generated

#ifndef CAFFE_PIXELSHUFFLE_LAYER_HPP_
#define CAFFE_PIXELSHUFFLE_LAYER_HPP_

#include <vector>

#include "caffe/blob.hpp"
#include "caffe/layer.hpp"
#include "caffe/proto/caffe.pb.h"

namespace caffe{
    
    template <typename Dtype>
    class PixelShuffleLayer : public Layer<Dtype>{
        public:
        explicit PixelShuffleLayer(const LayerParameter& param)
            :Layer<Dtype>(param) {}
        virtual void LayerSetUp(const vector<Blob<Dtype>*>& bottom,
            const vector<Blob<Dtype>*>& top);
        virtual void Reshape(const vector<Blob<Dtype>*>& bottom,
            const vector<Blob<Dtype>*>& top);
            
        virtual inline const char* type() const {return "PixelShuffle";}
        
        virtual void Forward_cpu(const vector<Blob<Dtype>*>& bottom,
            const vector<Blob<Dtype>*>& top);
        virtual void Forward_gpu(const vector<Blob<Dtype>*>& bottom,
            const vector<Blob<Dtype>*>& top);
        virtual void Backward_cpu(const vector<Blob<Dtype>*>& top,
            const vector<bool>& propagate_down, const vector<Blob<Dtype>*>& bottom) {}
        virtual void Backward_gpu(const vector<Blob<Dtype>*>& top,
            const vector<bool>& propagate_down, const vector<Blob<Dtype>*>& bottom);
            
        private:
        int upscale_factor_;
        };

}  // namespace caffe
#endif  // CAFFE_PIXELSHUFFLE_LAYER_HPP_

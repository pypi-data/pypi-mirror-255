import numpy as np
from plottergeist import make_hist

def compute_pulls(ref_counts:np.ndarray, counts:np.ndarray, counts_l:np.ndarray,
                  counts_h:np.ndarray)->np.ndarray:
  """
  This function takes an array of ref_counts (reference histogram) and three
  arrays of the objective histogram: counts, counts_l (counts' lower limit) and
  counts_h (counts' higher limit). It returns the pull of counts wrt ref_counts.
  """
  residuals = counts - ref_counts;
  # print("counts_l:", counts_l)
  # print("counts_h:", counts_h)
  pulls = np.where(residuals>0, residuals/counts_l, residuals/counts_h)
  return pulls

def compare_hist(data, fit, data_weights=None,
                 fit_weights=None, density=False, bins=None, *args, **kwargs):
  """
  This function compares to histograms in data=[ref, obj] with(/out) weights
  It returns two hisrogram ipo-objects, obj one with pulls, and both of them
  normalized to one.
  Parameters
  ----------
  data
  fit
  data_weights
  fit_weights
  density
  """
  _data = make_hist(data, weights=data_weights, density=density, bins=bins,
                    *args, **kwargs)
  _fit = make_hist(fit, weights=fit_weights, density=density, bins=_data.edges, *args,
                 **kwargs)

  assert _fit.norm != 0.0, f"The integral of the histogram of the PDF is 0. Check the values: {_fit.counts}"

  _data_norm = 1.0
  # _fit_norm = 1.0
  _fit_norm = _data.norm/_fit.norm

  # if scale_fit:
  #   _fit_norm *= _data.norm / _fit.norm

  if density:
    _data_norm = 1/_data.counts.sum()
    _fit_norm *= 1/_fit.counts.sum()
  _data = _data._replace(counts=_data.counts*_data_norm)
  _data = _data._replace(yerr=[y * _data_norm for y in _data.yerr])
  _fit = _fit._replace(counts=_fit.counts*_fit_norm)
  _fit = _fit._replace(yerr=[y * _fit_norm for y in _fit.yerr])
  # pulls = compute_pulls(_data.counts, _fit.counts, *_fit.yerr)
  pulls = compute_pulls(_fit.counts, _data.counts, *_data.yerr)

  return _data, _fit, pulls

#include <vector>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

std::vector<std::pair<float, int>> data;
std::vector<int> current(5, 0), best(5, 0);
float maximum = 0;

void go(int cur, int taken, float pts, int moneyLeft) {
    if (taken == 5) {
        if (pts > maximum) {
            maximum = pts;
            for (int i = 0; i < 5; ++i) {
                best[i] = current[i];
            }
        }
        return;
    }
    if (moneyLeft <= 140 || cur == static_cast<int>(data.size())) return;
    if (data[cur].second <= moneyLeft) {
        current[taken] = cur;
        go(cur + 1, taken + 1, pts + data[cur].first, moneyLeft - data[cur].second);
    }
    go(cur + 1, taken, pts, moneyLeft);
}

std::vector<int> best_subset(std::vector<float>& points, std::vector<int>& costs) {
    int size = static_cast<int>(points.size());
    data = std::vector<std::pair<float, int>>(size);
    for (int i = 0; i < size; ++i) data[i] = std::make_pair(points[i], costs[i]);
    go(0, 0, 0, 1000);
    return best;
}

PYBIND11_MODULE(fantasyalgo, handle) {
    handle.doc() = "Some algorithms for fantasy model.";
    handle.def("best_subset", &best_subset);
}

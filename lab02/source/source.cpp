#include <iostream>
#include <vector>
#include <iomanip>

using namespace std;

const double L = 1;             // ширина пластины в метрах
const double T0 = 20;           // температура слева
const double Tn = 80;           // температура справа
const double lambda = 400;      // теплопроводность
const double rho = 8920;        // плотность
const double c = 1.0;
const double observation_time = 2; // Время наблюдения эксперимента


double compute(double cur_dt, double cur_step)
{
    // Количество шагов по сетке
    int N = static_cast<int>(L / cur_step) + 1;

    // Массивчики температур и констант вычисления
    vector<double> T_old(N, T0);
    vector<double> T_new(N);
    vector<double> alpha(N);
    vector<double> beta(N);

    // Температура на границах
    T_old[0] = T0;
    T_old[N - 1] = T0;

    // Постоянные коэффициенты схемы
    double coeff = rho * c / cur_dt;
    double A = lambda / (cur_step * cur_step);
    double C = A;
    double B = 2 * A + coeff;

    // Количество шагов по времени. Математическое округление
    int n_dt = static_cast<int>(observation_time / cur_dt + 0.5);

    for (int dt = 0; dt < n_dt; dt++)
    {
        // Прямая прогонка
        alpha[0] = 0;
        beta[0] = T0;

        for (int i = 1; i <= N - 2; i++)
        {
            double denominator = B - C * alpha[i - 1];
            alpha[i] = A / denominator;
            double Fi = -coeff * T_old[i];
            beta[i] = (C * beta[i - 1] - Fi) / denominator;
        }

        // Обратная прогонка
        T_new[N - 1] = Tn;
        for (int i = N - 2; i >= 1; i--)
        {
            T_new[i] = alpha[i] * T_new[i + 1] + beta[i];
        }
        T_new[0] = T0;

        // Переход к следующему изменению dt
        T_old = T_new;
    }

    // Индекс центрального узла
    int i_center = static_cast<int>(N / 2 + 0.5);
    return T_old[i_center];
}

int main() {
    // Исследуемые шаги
    vector<double> dt_vals = { 0.1, 0.01, 0.001, 0.0001 };
    vector<double> step_vals = { 0.1, 0.01, 0.001, 0.0001 };

    // Вывод заголовка таблицы
    cout << fixed << setprecision(4);
    cout << "time step, sec \\ space step, meters";
    cout << endl;
    cout << "" << setw(17);
    for (double h : step_vals)
    {
        cout << h << "|" << setw(10);
    }
    cout << setw(1) << endl;

    // Заполнение таблицы
    for (double cur_dt : dt_vals)
    {
        cout << cur_dt << "|";
        for (double cur_step : step_vals)
        {
            double temp = compute(cur_dt, cur_step);
            cout << setw(10) << temp << "|";
        }
        cout << endl;
    }

    return 0;
}
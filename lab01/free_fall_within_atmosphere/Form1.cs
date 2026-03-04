using System.Collections.Specialized;
using System.Diagnostics;

namespace free_fall_within_atmosphere
{
    public partial class Form1 : Form
    {
        public Form1()
        {
            InitializeComponent();
        }

        decimal t, dt, x, y, v0, cosa, sina, S, m, k, velocity_x, velocity_y, max_height, max_distance;
        double angle;
        const decimal g = 9.81M;
        const decimal C = 0.15M;
        const decimal rho = 1.29M;
        const int max_graphics_count = 5;

        int cur_graphic_idx = -1;

        HashSet<decimal> computed_dt = new HashSet<decimal>();

        private void ClearGraphics(int graphics_count)
        {
            for (int i = 0; i < graphics_count; i++)
                MainChart.Series[i].Points.Clear();
        }


        private void StartButton_Click(object sender, EventArgs e)
        {
            if (!timer1.Enabled)
            {
                dt = TimeStepField.Value;
                // Выполняем расчеты, если еще не вычисляли для данного dt
                if (computed_dt.Contains(dt))
                {
                    LoggingListBox.Items.Add("Для текущего dt уже вычислено!");
                    return;
                }
                if (++cur_graphic_idx > (max_graphics_count - 1))
                {
                    LoggingListBox.Items.Add($"Превышено максимальное количество одновременных графиков на экране!");
                    return;
                }
                LoggingListBox.Items.Add($"Начало расчетов...");
                computed_dt.Add(dt);
                MainChart.Series.Add("dt = " + dt.ToString());
                MainChart.Series[cur_graphic_idx].ChartType = System.Windows.Forms.DataVisualization.Charting.SeriesChartType.Line;
                MainChart.Series[cur_graphic_idx].BorderWidth = 3;
                // Очищаем графики
                if (computed_dt.Count == 0)
                {
                    ClearGraphics(cur_graphic_idx+1);
                }
                // Блок с подготовительными вычислениями
                t = 0;
                x = 0;
                y = HeightField.Value;

                max_distance = x;
                max_height = y;

                v0 = VelocityField.Value;
                angle = (double)AngleField.Value * Math.PI / 180;
                cosa = (decimal)Math.Cos(angle);
                sina = (decimal)Math.Sin(angle);
                S = VolumeField.Value;
                m = MassField.Value;
                k = 0.5M * C * rho * S / m;
                velocity_x = v0 * cosa;
                velocity_y = v0 * sina;
                MainChart.Series[cur_graphic_idx].Points.AddXY(x, y);
                timer1.Start();
            }
            else
            {
                LoggingListBox.Items.Add("Остановитесь! Выполняются расчеты для текущего dt!");
            }

        }

        private void timer1_Tick(object sender, EventArgs e)
        {
            // Блок с основными расчетами
            t += dt;
            decimal velocity_vector = (decimal)Math.Sqrt((double)(velocity_x * velocity_x + velocity_y * velocity_y));
            velocity_x = velocity_x - k * velocity_x * velocity_vector * dt;
            velocity_y = velocity_y - (g + k * velocity_y * velocity_vector) * dt;
            x = x + velocity_x * dt;
            y = y + velocity_y * dt;
            max_distance = (x > max_distance) ? x : max_distance;
            max_height = (y > max_height) ? y : max_height;
            MainChart.Series[cur_graphic_idx].Points.AddXY(x, y);
            if (y <= 0)
            {
                LoggingListBox.Items.Add($"------------------------------");
                LoggingListBox.Items.Add($"dt = {dt}");
                LoggingListBox.Items.Add($"Скорость в конечной точке = {velocity_vector}");
                LoggingListBox.Items.Add($"Максимальная высота = {max_height}");
                LoggingListBox.Items.Add($"Дальность полета = {max_distance}");
                LoggingListBox.Items.Add($"------------------------------");
                timer1.Stop();
            }
        }

        private void ClearButton_Click(object sender, EventArgs e)
        {
            if (timer1.Enabled)
                return;
            // Очистка графиков и иных элементов от результатов предыдущих расчетов
            cur_graphic_idx = -1;
            LoggingListBox.Items.Clear();
            ClearGraphics(cur_graphic_idx+1);
            computed_dt.Clear();
            MainChart.Series.Clear();
        }
    }
}

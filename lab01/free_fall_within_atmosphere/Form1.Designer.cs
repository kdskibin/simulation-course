namespace free_fall_within_atmosphere
{
    partial class Form1
    {
        /// <summary>
        ///  Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        ///  Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        ///  Required method for Designer support - do not modify
        ///  the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            components = new System.ComponentModel.Container();
            System.Windows.Forms.DataVisualization.Charting.ChartArea chartArea1 = new System.Windows.Forms.DataVisualization.Charting.ChartArea();
            System.Windows.Forms.DataVisualization.Charting.Legend legend1 = new System.Windows.Forms.DataVisualization.Charting.Legend();
            HeightLabel = new Label();
            HeightField = new NumericUpDown();
            AngleField = new NumericUpDown();
            VolumeField = new NumericUpDown();
            Speed = new Label();
            MassField = new NumericUpDown();
            MassLabel = new Label();
            VelocityField = new NumericUpDown();
            SizeLabel = new Label();
            StartButton = new Button();
            MainChart = new System.Windows.Forms.DataVisualization.Charting.Chart();
            AngleLabel = new Label();
            TimeStepField = new NumericUpDown();
            TimeStep = new Label();
            timer1 = new System.Windows.Forms.Timer(components);
            LoggingListBox = new ListBox();
            ClearButton = new Button();
            ((System.ComponentModel.ISupportInitialize)HeightField).BeginInit();
            ((System.ComponentModel.ISupportInitialize)AngleField).BeginInit();
            ((System.ComponentModel.ISupportInitialize)VolumeField).BeginInit();
            ((System.ComponentModel.ISupportInitialize)MassField).BeginInit();
            ((System.ComponentModel.ISupportInitialize)VelocityField).BeginInit();
            ((System.ComponentModel.ISupportInitialize)MainChart).BeginInit();
            ((System.ComponentModel.ISupportInitialize)TimeStepField).BeginInit();
            SuspendLayout();
            // 
            // HeightLabel
            // 
            HeightLabel.AutoSize = true;
            HeightLabel.Location = new Point(12, 9);
            HeightLabel.Name = "HeightLabel";
            HeightLabel.Size = new Size(109, 15);
            HeightLabel.TabIndex = 0;
            HeightLabel.Text = "Начальная высота";
            // 
            // HeightField
            // 
            HeightField.Location = new Point(136, 7);
            HeightField.Maximum = new decimal(new int[] { 1000, 0, 0, 0 });
            HeightField.Name = "HeightField";
            HeightField.Size = new Size(76, 23);
            HeightField.TabIndex = 1;
            HeightField.TextAlign = HorizontalAlignment.Center;
            // 
            // AngleField
            // 
            AngleField.Location = new Point(136, 36);
            AngleField.Maximum = new decimal(new int[] { 90, 0, 0, 0 });
            AngleField.Name = "AngleField";
            AngleField.Size = new Size(76, 23);
            AngleField.TabIndex = 3;
            AngleField.TextAlign = HorizontalAlignment.Center;
            AngleField.Value = new decimal(new int[] { 45, 0, 0, 0 });
            // 
            // VolumeField
            // 
            VolumeField.Location = new Point(282, 7);
            VolumeField.Maximum = new decimal(new int[] { 1000, 0, 0, 0 });
            VolumeField.Name = "VolumeField";
            VolumeField.Size = new Size(73, 23);
            VolumeField.TabIndex = 5;
            VolumeField.TextAlign = HorizontalAlignment.Center;
            VolumeField.Value = new decimal(new int[] { 1, 0, 0, 0 });
            // 
            // Speed
            // 
            Speed.AutoSize = true;
            Speed.Location = new Point(375, 9);
            Speed.Name = "Speed";
            Speed.Size = new Size(120, 15);
            Speed.TabIndex = 4;
            Speed.Text = "Начальная скорость";
            // 
            // MassField
            // 
            MassField.Location = new Point(282, 36);
            MassField.Maximum = new decimal(new int[] { 1000, 0, 0, 0 });
            MassField.Minimum = new decimal(new int[] { 1, 0, 0, 327680 });
            MassField.Name = "MassField";
            MassField.Size = new Size(73, 23);
            MassField.TabIndex = 7;
            MassField.TextAlign = HorizontalAlignment.Center;
            MassField.Value = new decimal(new int[] { 2, 0, 0, 0 });
            // 
            // MassLabel
            // 
            MassLabel.AutoSize = true;
            MassLabel.Location = new Point(234, 38);
            MassLabel.Name = "MassLabel";
            MassLabel.Size = new Size(42, 15);
            MassLabel.TabIndex = 6;
            MassLabel.Text = "Масса";
            // 
            // VelocityField
            // 
            VelocityField.Location = new Point(501, 7);
            VelocityField.Maximum = new decimal(new int[] { 1000, 0, 0, 0 });
            VelocityField.Name = "VelocityField";
            VelocityField.Size = new Size(69, 23);
            VelocityField.TabIndex = 9;
            VelocityField.TextAlign = HorizontalAlignment.Center;
            VelocityField.Value = new decimal(new int[] { 10, 0, 0, 0 });
            // 
            // SizeLabel
            // 
            SizeLabel.AutoSize = true;
            SizeLabel.Location = new Point(231, 9);
            SizeLabel.Name = "SizeLabel";
            SizeLabel.Size = new Size(45, 15);
            SizeLabel.TabIndex = 8;
            SizeLabel.Text = "Объем";
            // 
            // StartButton
            // 
            StartButton.BackColor = Color.OrangeRed;
            StartButton.Location = new Point(587, 5);
            StartButton.Name = "StartButton";
            StartButton.Size = new Size(75, 23);
            StartButton.TabIndex = 12;
            StartButton.Text = "Пуск";
            StartButton.UseVisualStyleBackColor = false;
            StartButton.Click += StartButton_Click;
            // 
            // MainChart
            // 
            chartArea1.AxisX.Minimum = 0D;
            chartArea1.AxisY.Minimum = 0D;
            chartArea1.Name = "ChartArea1";
            MainChart.ChartAreas.Add(chartArea1);
            legend1.Name = "Legend1";
            MainChart.Legends.Add(legend1);
            MainChart.Location = new Point(12, 65);
            MainChart.Name = "MainChart";
            MainChart.Size = new Size(776, 373);
            MainChart.TabIndex = 13;
            MainChart.Text = "chart1";
            // 
            // AngleLabel
            // 
            AngleLabel.AutoSize = true;
            AngleLabel.Location = new Point(12, 36);
            AngleLabel.Name = "AngleLabel";
            AngleLabel.Size = new Size(75, 15);
            AngleLabel.TabIndex = 14;
            AngleLabel.Text = "Угол броска";
            // 
            // TimeStepField
            // 
            TimeStepField.DecimalPlaces = 4;
            TimeStepField.Increment = new decimal(new int[] { 1, 0, 0, 262144 });
            TimeStepField.Location = new Point(501, 36);
            TimeStepField.Maximum = new decimal(new int[] { 10, 0, 0, 0 });
            TimeStepField.Name = "TimeStepField";
            TimeStepField.Size = new Size(69, 23);
            TimeStepField.TabIndex = 16;
            TimeStepField.TextAlign = HorizontalAlignment.Center;
            // 
            // TimeStep
            // 
            TimeStep.AutoSize = true;
            TimeStep.Location = new Point(375, 38);
            TimeStep.Name = "TimeStep";
            TimeStep.Size = new Size(120, 15);
            TimeStep.TabIndex = 15;
            TimeStep.Text = "Шаг моделирования";
            // 
            // timer1
            // 
            timer1.Interval = 1;
            timer1.Tick += timer1_Tick;
            // 
            // LoggingListBox
            // 
            LoggingListBox.FormattingEnabled = true;
            LoggingListBox.Location = new Point(12, 444);
            LoggingListBox.Name = "LoggingListBox";
            LoggingListBox.Size = new Size(776, 154);
            LoggingListBox.TabIndex = 18;
            // 
            // ClearButton
            // 
            ClearButton.Location = new Point(587, 36);
            ClearButton.Name = "ClearButton";
            ClearButton.Size = new Size(75, 23);
            ClearButton.TabIndex = 19;
            ClearButton.Text = "Очистить";
            ClearButton.UseVisualStyleBackColor = true;
            ClearButton.Click += ClearButton_Click;
            // 
            // Form1
            // 
            AutoScaleDimensions = new SizeF(7F, 15F);
            AutoScaleMode = AutoScaleMode.Font;
            ClientSize = new Size(800, 610);
            Controls.Add(ClearButton);
            Controls.Add(LoggingListBox);
            Controls.Add(TimeStepField);
            Controls.Add(TimeStep);
            Controls.Add(AngleLabel);
            Controls.Add(MainChart);
            Controls.Add(StartButton);
            Controls.Add(VelocityField);
            Controls.Add(SizeLabel);
            Controls.Add(MassField);
            Controls.Add(MassLabel);
            Controls.Add(VolumeField);
            Controls.Add(Speed);
            Controls.Add(AngleField);
            Controls.Add(HeightField);
            Controls.Add(HeightLabel);
            Name = "Form1";
            StartPosition = FormStartPosition.CenterScreen;
            Text = "Free fall within atmosphere";
            ((System.ComponentModel.ISupportInitialize)HeightField).EndInit();
            ((System.ComponentModel.ISupportInitialize)AngleField).EndInit();
            ((System.ComponentModel.ISupportInitialize)VolumeField).EndInit();
            ((System.ComponentModel.ISupportInitialize)MassField).EndInit();
            ((System.ComponentModel.ISupportInitialize)VelocityField).EndInit();
            ((System.ComponentModel.ISupportInitialize)MainChart).EndInit();
            ((System.ComponentModel.ISupportInitialize)TimeStepField).EndInit();
            ResumeLayout(false);
            PerformLayout();
        }

        #endregion

        private Label HeightLabel;
        private NumericUpDown HeightField;
        private NumericUpDown AngleField;
        private NumericUpDown VolumeField;
        private Label Speed;
        private NumericUpDown MassField;
        private Label MassLabel;
        private NumericUpDown VelocityField;
        private Label SizeLabel;
        private Button StartButton;
        private System.Windows.Forms.DataVisualization.Charting.Chart MainChart;
        private Label AngleLabel;
        private NumericUpDown TimeStepField;
        private Label TimeStep;
        private System.Windows.Forms.Timer timer1;
        private ListBox LoggingListBox;
        private Button ClearButton;
    }
}

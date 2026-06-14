import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import '../../models/position.dart';
import '../../services/firestore_service.dart';

enum PeriodFilter { week1, month1, month3, month6, year1, all }

extension PeriodFilterExt on PeriodFilter {
  String get label => switch (this) {
        PeriodFilter.week1 => '1주',
        PeriodFilter.month1 => '1달',
        PeriodFilter.month3 => '3달',
        PeriodFilter.month6 => '6달',
        PeriodFilter.year1 => '1년',
        PeriodFilter.all => '전체',
      };

  DateTime? get since {
    final now = DateTime.now();
    return switch (this) {
      PeriodFilter.week1 => now.subtract(const Duration(days: 7)),
      PeriodFilter.month1 => DateTime(now.year, now.month - 1, now.day),
      PeriodFilter.month3 => DateTime(now.year, now.month - 3, now.day),
      PeriodFilter.month6 => DateTime(now.year, now.month - 6, now.day),
      PeriodFilter.year1 => DateTime(now.year - 1, now.month, now.day),
      PeriodFilter.all => null,
    };
  }
}

class ChartScreen extends StatefulWidget {
  const ChartScreen({super.key});

  @override
  State<ChartScreen> createState() => _ChartScreenState();
}

class _ChartScreenState extends State<ChartScreen> {
  PeriodFilter _filter = PeriodFilter.all;

  List<Position> _applyFilter(List<Position> positions) {
    final since = _filter.since;
    if (since == null) return positions;
    return positions
        .where((p) => p.exitDate != null && p.exitDate!.isAfter(since))
        .toList();
  }

  @override
  Widget build(BuildContext context) {
    final service = FirestoreService();

    return StreamBuilder<List<Position>>(
      stream: service.positionsStream(),
      builder: (context, snapshot) {
        final all = snapshot.data ?? [];
        final closed = all
            .where((p) => p.status == 'closed' && p.returnRate != null)
            .toList()
          ..sort((a, b) => (a.exitDate ?? a.entryDate)
              .compareTo(b.exitDate ?? b.entryDate));
        final filtered = _applyFilter(closed);

        return Column(
          children: [
            // 기간 필터 칩
            SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              padding: const EdgeInsets.fromLTRB(12, 12, 12, 0),
              child: Row(
                children: PeriodFilter.values.map((f) {
                  final selected = _filter == f;
                  return Padding(
                    padding: const EdgeInsets.only(right: 8),
                    child: FilterChip(
                      label: Text(f.label),
                      selected: selected,
                      onSelected: (_) => setState(() => _filter = f),
                    ),
                  );
                }).toList(),
              ),
            ),
            Expanded(
              child: filtered.isEmpty
                  ? Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          const Icon(Icons.bar_chart, size: 64, color: Colors.grey),
                          const SizedBox(height: 12),
                          Text(
                            closed.isEmpty
                                ? '정리된 포지션이 없습니다.'
                                : '${_filter.label} 기간에 정리된 포지션이 없습니다.',
                            style: const TextStyle(color: Colors.grey),
                          ),
                        ],
                      ),
                    )
                  : ListView(
                      padding: const EdgeInsets.all(12),
                      children: [
                        _ReturnRateBarChart(positions: filtered),
                        const SizedBox(height: 16),
                        _CumulativePnlLineChart(positions: filtered),
                      ],
                    ),
            ),
          ],
        );
      },
    );
  }
}

// ── 수익률 막대 차트 ────────────────────────────────────────────
class _ReturnRateBarChart extends StatelessWidget {
  final List<Position> positions;
  const _ReturnRateBarChart({required this.positions});

  /// 동일 종목 묶어서 총 수익률 계산 (총 손익 / 총 투자금 × 100)
  List<MapEntry<String, double>> _grouped() {
    final map = <String, ({double totalPnl, double totalInvested})>{};
    for (final p in positions) {
      if (p.exitPrice == null) continue;
      final pnl = (p.exitPrice! - p.entryPrice) * p.quantity;
      final invested = p.entryPrice * p.quantity;
      final prev = map[p.symbol];
      map[p.symbol] = (
        totalPnl: (prev?.totalPnl ?? 0) + pnl,
        totalInvested: (prev?.totalInvested ?? 0) + invested,
      );
    }
    return map.entries
        .map((e) => MapEntry(
            e.key,
            e.value.totalInvested == 0
                ? 0.0
                : e.value.totalPnl / e.value.totalInvested * 100))
        .toList()
      ..sort((a, b) => b.value.compareTo(a.value));
  }

  @override
  Widget build(BuildContext context) {
    final grouped = _grouped();
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('종목별 총 수익률',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
            Text('${grouped.length}개 종목',
                style: const TextStyle(color: Colors.grey, fontSize: 12)),
            const SizedBox(height: 16),
            SizedBox(
              height: 220,
              child: BarChart(
                BarChartData(
                  alignment: BarChartAlignment.spaceAround,
                  maxY: _maxY(grouped),
                  minY: _minY(grouped),
                  barGroups: grouped.asMap().entries.map((e) {
                    final rate = e.value.value;
                    return BarChartGroupData(
                      x: e.key,
                      barRods: [
                        BarChartRodData(
                          toY: rate,
                          color: rate >= 0 ? Colors.blue : Colors.red,
                          width: _barWidth(grouped.length),
                          borderRadius: rate >= 0
                              ? const BorderRadius.vertical(top: Radius.circular(4))
                              : const BorderRadius.vertical(bottom: Radius.circular(4)),
                        ),
                      ],
                    );
                  }).toList(),
                  titlesData: FlTitlesData(
                    leftTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        reservedSize: 44,
                        getTitlesWidget: (v, _) => Text(
                          '${v.toStringAsFixed(0)}%',
                          style: const TextStyle(fontSize: 10),
                        ),
                      ),
                    ),
                    bottomTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        getTitlesWidget: (v, _) {
                          final idx = v.toInt();
                          if (idx < 0 || idx >= grouped.length) return const SizedBox.shrink();
                          return Padding(
                            padding: const EdgeInsets.only(top: 4),
                            child: Text(grouped[idx].key,
                                style: const TextStyle(fontSize: 9),
                                overflow: TextOverflow.ellipsis),
                          );
                        },
                      ),
                    ),
                    topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                    rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                  ),
                  gridData: FlGridData(drawVerticalLine: false, horizontalInterval: _gridInterval(grouped)),
                  borderData: FlBorderData(show: false),
                  barTouchData: BarTouchData(
                    touchTooltipData: BarTouchTooltipData(
                      getTooltipItem: (group, _, rod, __) {
                        final entry = grouped[group.x];
                        return BarTooltipItem(
                          '${entry.key}\n${rod.toY >= 0 ? '+' : ''}${rod.toY.toStringAsFixed(2)}%',
                          const TextStyle(color: Colors.white, fontSize: 12),
                        );
                      },
                    ),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  double _maxY(List<MapEntry<String, double>> g) {
    final max = g.map((e) => e.value).reduce((a, b) => a > b ? a : b);
    return (max * 1.3).ceilToDouble().clamp(5.0, double.infinity);
  }

  double _minY(List<MapEntry<String, double>> g) {
    final min = g.map((e) => e.value).reduce((a, b) => a < b ? a : b);
    return min < 0 ? (min * 1.3).floorToDouble().clamp(double.negativeInfinity, -5.0) : 0;
  }

  double _gridInterval(List<MapEntry<String, double>> g) {
    final range = _maxY(g) - _minY(g);
    if (range <= 20) return 5;
    if (range <= 50) return 10;
    return 20;
  }

  double _barWidth(int count) {
    if (count <= 5) return 24;
    if (count <= 10) return 16;
    return 10;
  }
}

// ── 누적 손익 라인 차트 ──────────────────────────────────────────
class _CumulativePnlLineChart extends StatelessWidget {
  final List<Position> positions;
  const _CumulativePnlLineChart({required this.positions});

  List<FlSpot> _spots() {
    double cum = 0;
    final spots = <FlSpot>[const FlSpot(0, 0)];
    for (int i = 0; i < positions.length; i++) {
      cum += positions[i].realizedPnl ?? 0;
      spots.add(FlSpot((i + 1).toDouble(), cum));
    }
    return spots;
  }

  @override
  Widget build(BuildContext context) {
    final spots = _spots();
    final maxY = spots.map((s) => s.y).reduce((a, b) => a > b ? a : b);
    final minY = spots.map((s) => s.y).reduce((a, b) => a < b ? a : b);
    final pad = ((maxY - minY) * 0.2).abs().clamp(10000.0, double.infinity);
    final finalPnl = spots.last.y;
    final color = finalPnl >= 0 ? Colors.blue : Colors.red;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text('누적 실현 손익',
                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
                Text(
                  '${finalPnl >= 0 ? '+' : ''}₩${_fmt(finalPnl)}',
                  style: TextStyle(fontWeight: FontWeight.bold, color: color),
                ),
              ],
            ),
            const SizedBox(height: 16),
            SizedBox(
              height: 200,
              child: LineChart(
                LineChartData(
                  minY: minY - pad,
                  maxY: maxY + pad,
                  lineBarsData: [
                    LineChartBarData(
                      spots: spots,
                      isCurved: true,
                      color: color,
                      barWidth: 2.5,
                      dotData: FlDotData(
                        getDotPainter: (spot, _, __, ___) => FlDotCirclePainter(
                          radius: 3,
                          color: color,
                          strokeWidth: 0,
                        ),
                      ),
                      belowBarData: BarAreaData(
                        show: true,
                        color: color.withAlpha(30),
                      ),
                    ),
                  ],
                  titlesData: FlTitlesData(
                    leftTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        reservedSize: 56,
                        getTitlesWidget: (v, _) =>
                            Text(_shortFmt(v), style: const TextStyle(fontSize: 10)),
                      ),
                    ),
                    bottomTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        interval: (positions.length / 4).ceilToDouble(),
                        getTitlesWidget: (v, _) {
                          final idx = v.toInt() - 1;
                          if (idx < 0 || idx >= positions.length) {
                            return const Text('시작', style: TextStyle(fontSize: 9));
                          }
                          final d = positions[idx].exitDate;
                          if (d == null) return const SizedBox.shrink();
                          return Text('${d.month}/${d.day}',
                              style: const TextStyle(fontSize: 9));
                        },
                      ),
                    ),
                    topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                    rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                  ),
                  gridData: const FlGridData(drawVerticalLine: false),
                  borderData: FlBorderData(show: false),
                  lineTouchData: LineTouchData(
                    touchTooltipData: LineTouchTooltipData(
                      getTooltipItems: (spots) => spots
                          .map((s) => LineTooltipItem(
                                '₩${_fmt(s.y)}',
                                const TextStyle(color: Colors.white, fontSize: 12),
                              ))
                          .toList(),
                    ),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  String _fmt(double v) => v.abs()
      .toStringAsFixed(0)
      .replaceAllMapped(RegExp(r'(\d)(?=(\d{3})+$)'), (m) => '${m[1]},');

  String _shortFmt(double v) {
    if (v.abs() >= 1000000) return '${(v / 1000000).toStringAsFixed(1)}M';
    if (v.abs() >= 1000) return '${(v / 1000).toStringAsFixed(0)}K';
    return v.toStringAsFixed(0);
  }
}

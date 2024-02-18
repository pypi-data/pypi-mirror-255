#pragma once

#include <cstdint>

#include "akida/np.h"
#include "engine/dma.h"

namespace akida {

namespace dma {

enum class Target {
  CnpFilter,
  CnpFilterCompact,  // Only in V2 (uses 3x32b to format 100 bit)
  InputShifts,       // Only in V2
  CnpLearnThres,     // Only in v1
  CnpFireThres,      // Only in v1
  CnpBiasOutScale,   // Only in V2
  FnpWeights,
  NpRegisters,
  HrcRegisters,
  HrcSram,
};

// format header (must be at least 2 elements) to contain a DMA header
void format_config_header(uint32_t* header, const struct np::Ident& np,
                          Target target, uint32_t size, uint16_t dest_addr,
                          bool xl = false);

uint32_t parse_config_read_size(const wbuffer& read_header);

bool config_block_size_needs_xl(uint32_t block_size);

// Size of address
constexpr uint32_t kXlIncrementSz = 16;
constexpr uint32_t kConfigReadPacketHdrSz = 1;
constexpr uint32_t kConfigReadPacketOffset = 32;
constexpr uint32_t kConfigNpHeaderWordSize = 2;
constexpr uint32_t kConfigNpHeaderByteSize =
    kConfigNpHeaderWordSize * sizeof(dma::w32);

}  // namespace dma

}  // namespace akida
